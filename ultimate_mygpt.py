#!/usr/bin/env python
"""
Ultimate MyGPT-Paper Analyzer - Ultimate Version (2.0)
・PubMed/PMC, arXiv, bioRxiv等主要ソースから論文を自動取得・解析
・XML解析、テキストクレンジング、セクション認識による本文抽出
・高度なテキストチャンク化、重複オーバーラップ処理
・Transformerによる要約生成（多段階要約対応）
・埋め込み生成（SciBERT/SPECTER/All-MiniLM選択可能）でFAISS検索連携（拡張可能）
・FastAPIによるREST API提供 (/search, /paper/{id}, /export, /embed, /health, /version, /status, /log, /search_arxiv)
・非同期処理、バッチ処理、キャッシュ、リトライ戦略を実装
・pydanticによる厳格なスキーマ管理、ドキュメント自動生成
・GitHub管理、無料ホスティング＋CI/CD自動更新、MyGPTアクション連携を前提
"""

# 基本モジュールのインポート
import os, re, json, time, math, uuid, base64, logging, asyncio, datetime, platform
import numpy as np  # NumPy を np として利用するためのインポート
from typing import List, Dict, Any, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# NLP / MLライブラリ
import nltk, spacy, pysbd, torch
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss

# --- 設定管理 ---
class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(".")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "outputs")
    CACHE_DIR: str = os.path.join(BASE_DIR, "cache")
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")
    MODEL_DIR: str = os.path.join(BASE_DIR, "models")
    TEMP_DIR: str = os.path.join(BASE_DIR, "temp")
    META_DIR: str = os.path.join(OUTPUT_DIR, "metadata")
    MAX_RETRIES: int = 5
    RETRY_DELAY: float = 2.0
    TIMEOUT: float = 30.0
    API_RATE_LIMIT: float = 0.34
    NUM_PAPERS_PER_QUERY: int = 50
    MAX_TOTAL_PAPERS: int = 100
    MIN_YEAR: int = 2015
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 2000
    TARGET_CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 50
    QUALITY_THRESHOLD: int = 30
    SIMILARITY_THRESHOLD: float = 0.85
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    EMBEDDING_MODEL: str = "default"
    NCBI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

# --- ログ設定 ---
os.makedirs(settings.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(settings.LOG_DIR, "pubmed_rag.log"), mode="a")]
)
logger = logging.getLogger(__name__)

# --- NLTK初期化 ---
for pkg in ["punkt", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

# --- ユーティリティ関数 ---
def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def truncate_text(text: str, max_length: int = 1000) -> str:
    return text if len(text) <= max_length else text[:max_length-3] + "..."

# --- モデル・パイプライン管理 ---
class ModelLoader:
    """各種NLPモデルのロード・管理クラス。埋め込みは設定によりSciBERT, SPECTERなどに切替可能。"""
    def __init__(self):
        self.semantic_model: Optional[SentenceTransformer] = None
        self.summarizer: Optional[Any] = None
        self.tokenizer_summary: Optional[Any] = None
        self.classifier: Optional[Any] = None
        self.qa_generator: Optional[Any] = None
        self.ner_model: Optional[Any] = None
        self.nlp: Optional[Any] = None

    def load_all(self) -> bool:
        try:
            logger.info("Loading embedding model...")
            if settings.EMBEDDING_MODEL == "scibert":
                self.semantic_model = SentenceTransformer('allenai/scibert_scivocab_uncased')
            elif settings.EMBEDDING_MODEL == "specter":
                self.semantic_model = SentenceTransformer('allenai/specter')
            else:
                self.semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loading summarization model...")
            model_name = "t5-small"
            self.tokenizer_summary = AutoTokenizer.from_pretrained(model_name)
            self.summarizer = pipeline("summarization", model=model_name, device=0 if torch.cuda.is_available() else -1)
            logger.info("Loading zero-shot classification model...")
            self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0 if torch.cuda.is_available() else -1)
            logger.info("Loading QA generation model...")
            self.qa_generator = pipeline("text2text-generation", model="t5-small", device=0 if torch.cuda.is_available() else -1)
            logger.info("Loading NER model with spaCy...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            self.ner_model = self.nlp
            logger.info("All models loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

model_loader = ModelLoader()
models_loaded = model_loader.load_all()

# --- FAISSインデックス (拡張性のための基礎) ---
faiss_index = None
def build_faiss_index(embeddings: List[np.ndarray]) -> Any:
    d = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(d)
    index.add(np.stack(embeddings))
    return index

# --- Pydanticモデル定義 ---
class Chunk(BaseModel):
    id: int
    text: str
    embedding: List[float]

class ArticleSummary(BaseModel):
    pmid: str = Field(..., description="PubMed ID")
    title: str = Field(..., description="Article title")
    authors: List[str] = Field(..., description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    year: Optional[int] = Field(None, description="Publication year")
    abstract: Optional[str] = Field(None, description="Abstract text")
    citation: Optional[str] = Field(None, description="Citation text")

class PaperData(BaseModel):
    summary: ArticleSummary
    full_text: str = Field(..., description="Cleaned full text (or abstract fallback)")
    processed_summary: str = Field(..., description="Generated summary via Transformer")
    tags: List[str] = Field([], description="Extracted key tags")
    chunks: List[Chunk] = Field([], description="Text chunks with corresponding embeddings")

# --- テキストチャンク化 ---
class SmartChunker:
    def __init__(self):
        try:
            self.segmenter = pysbd.Segmenter(language="en", clean=True)
        except Exception:
            self.segmenter = None

    def split_sentences(self, text: str) -> List[str]:
        if not text.strip():
            return []
        if self.segmenter:
            try:
                return self.segmenter.segment(text)
            except Exception:
                pass
        return nltk.sent_tokenize(text)

    def chunk_text(self, text: str, target_size: int = settings.TARGET_CHUNK_SIZE,
                   overlap: int = settings.CHUNK_OVERLAP) -> List[str]:
        sentences = self.split_sentences(text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk.split()) + len(sentence.split()) <= target_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        # オーバーラップ処理
        final_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev = final_chunks[-1]
                combined = (prev[-overlap:] + " " + chunk).strip()
                final_chunks[-1] = prev + "\n" + combined
            else:
                final_chunks.append(chunk)
        return final_chunks

# --- 外部API連携: PubMed など ---
class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    def __init__(self, api_key: Optional[str] = settings.NCBI_API_KEY):
        self.api_key = api_key

    async def search(self, query: str, retmax: int = settings.NUM_PAPERS_PER_QUERY) -> (List[str], int):
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax
        }
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{self.BASE_URL}/esearch.fcgi"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=settings.TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
        result = data.get("esearchresult", {})
        count = int(result.get("count", 0))
        id_list = result.get("idlist", [])
        return id_list, count

    async def fetch_details(self, ids: List[str]) -> List[ArticleSummary]:
        if not ids:
            return []
        id_str = ",".join(ids)
        params = {
            "db": "pubmed",
            "id": id_str,
            "retmode": "xml"
        }
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{self.BASE_URL}/efetch.fcgi"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=settings.TIMEOUT)
            resp.raise_for_status()
            xml_content = resp.text
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            raise HTTPException(status_code=502, detail="Failed to parse XML response from PubMed")
        articles = []
        for article in root.findall(".//PubmedArticle"):
            pmid_elem = article.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
            title_elem = article.find(".//ArticleTitle")
            title = "".join(title_elem.itertext()).strip() if title_elem is not None else "No title"
            abstract_elems = article.findall(".//AbstractText")
            abstract = "\n".join(["".join(ab.itertext()).strip() for ab in abstract_elems]) if abstract_elems else None
            authors = []
            for auth in article.findall(".//AuthorList/Author"):
                last = auth.findtext("LastName")
                first = auth.findtext("ForeName")
                if last and first:
                    authors.append(f"{last}, {first}")
                elif last:
                    authors.append(last)
                else:
                    collab = auth.findtext("CollectiveName")
                    if collab:
                        authors.append(collab)
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown"
            year_elem = article.find(".//Journal/JournalIssue/PubDate/Year")
            year = int(year_elem.text) if year_elem is not None and year_elem.text.isdigit() else None
            citation = f"{authors[0] if authors else 'Unknown'} et al. ({year}). {title}. {journal}."
            articles.append(ArticleSummary(
                pmid=pmid,
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                citation=citation
            ))
        return articles

# --- 新規: ArxivClient の定義 ---
import xml.etree.ElementTree as ET  # 既にインポートされていなければ追加
class ArxivClient:
    BASE_URL = "http://export.arxiv.org/api/query"
    
    async def search(self, query: str, max_results: int = 10) -> List[ArticleSummary]:
        # URL例: http://export.arxiv.org/api/query?search_query=all:がん&max_results=10
        url = f"{self.BASE_URL}?search_query=all:{query}&max_results={max_results}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=settings.TIMEOUT)
            resp.raise_for_status()
            xml_content = resp.text
        # XML をパース
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(xml_content)
        articles = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else "No title"
            summary_text = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
            authors = [author.find('atom:name', ns).text.strip() for author in entry.findall('atom:author', ns)]
            journal = "arXiv"
            published = entry.find('atom:published', ns).text.strip() if entry.find('atom:published', ns) is not None else ""
            year = int(published[:4]) if published and published[:4].isdigit() else None
            articles.append(ArticleSummary(
                pmid="",
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=summary_text,
                citation=f"{authors[0] if authors else 'Unknown'} et al. ({year}). {title}. {journal}."
            ))
        return articles

# --- FastAPI インスタンスの定義 ---
app = FastAPI(
    title="Ultimate MyGPT-Paper Analyzer API",
    description="PubMed/PMC, arXiv, bioRxiv 論文の検索、解析、要約、チャンク化、埋め込み生成を提供するAPI。MyGPTのRAG連携用学習データとして利用可能。",
    version="2.0.0"
)

# --- CORS ミドルウェアと静的ファイルの設定 ---
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ルートエンドポイントの定義 ---
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# --- その他のエンドポイントの定義 ---
@app.post("/log", tags=["Logging"])
async def log_interaction(request: Request):
    data = await request.json()
    log_dir = os.path.join(settings.LOG_DIR, "user_interactions")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "interactions.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    logger.info("User interaction logged.")
    return {"message": "Log received"}

@app.get("/version", tags=["Info"])
def version_info():
    version = "2.0.0"
    build_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os_info = platform.platform()
    return {"version": version, "build_time": build_time, "platform": os_info}

@app.get("/status", tags=["Info"])
def status_info():
    return {
        "status": "running",
        "uptime": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "base_dir": os.getcwd()
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}

class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[Dict[str, Any]]

@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_articles(query: str, max_results: int = 10):
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    max_results = min(max_results, 100)
    pubmed = PubMedClient(api_key=settings.NCBI_API_KEY)
    ids, count = await pubmed.search(query, retmax=max_results)
    articles = await pubmed.fetch_details(ids)
    results = [{"pmid": art.pmid, "title": art.title, "journal": art.journal, "year": art.year} for art in articles]
    return SearchResponse(query=query, count=count, results=results)

# 新規エンドポイント: arXiv の検索
@app.get("/search_arxiv", tags=["Search"])
async def search_arxiv(query: str, max_results: int = 10):
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    arxiv_client = ArxivClient()
    articles = await arxiv_client.search(query, max_results)
    results = [{"title": art.title, "authors": art.authors, "year": art.year, "abstract": art.abstract} for art in articles]
    return {"query": query, "count": len(results), "results": results}

@app.get("/paper/{pmid}", response_model=PaperData, tags=["Paper"])
async def get_paper(pmid: str):
    pubmed = PubMedClient(api_key=settings.NCBI_API_KEY)
    articles = await pubmed.fetch_details([pmid])
    if not articles:
        raise HTTPException(status_code=404, detail=f"No article found for PMID {pmid}")
    # process_paper 関数は要約生成、チャンク化などを実施する補助関数です（定義済みの前提）
    paper = process_paper(articles[0])
    return paper

@app.get("/export", response_model=List[PaperData], tags=["Export"])
async def export(query: str, max_results: int = 10):
    articles = await export_articles(query, retmax=max_results)
    return articles

@app.get("/embed", tags=["Embedding"])
async def get_embedding(pmid: Optional[str] = None, text: Optional[str] = None):
    if pmid:
        pubmed = PubMedClient(api_key=settings.NCBI_API_KEY)
        articles = await pubmed.fetch_details([pmid])
        if not articles:
            raise HTTPException(status_code=404, detail=f"No article found for PMID {pmid}")
        vec = model_loader.semantic_model.encode(articles[0].abstract or "")
        return {"pmid": pmid, "embedding": vec.tolist()}
    elif text:
        vec = model_loader.semantic_model.encode(text)
        return {"text": text, "embedding": vec.tolist()}
    else:
        raise HTTPException(status_code=400, detail="Provide either pmid or text for embedding.")

@app.post("/update", tags=["Maintenance"])
async def update_database(background_tasks: BackgroundTasks):
    async def update_task():
        topics = ["CD73", "adenosine", "cancer immunotherapy", "tumor microenvironment"]
        all_ids = []
        async with httpx.AsyncClient() as client:
            for topic in topics:
                try:
                    pm_client = PubMedClient(api_key=settings.NCBI_API_KEY)
                    ids, _ = await pm_client.search(topic)
                    all_ids.extend(["pubmed:" + pid for pid in ids])
                except Exception as e:
                    logger.error(f"Error updating topic {topic}: {e}")
        unique_ids = list(dict.fromkeys(all_ids))
        update_file = os.path.join(settings.META_DIR, "processed_ids.json")
        with open(update_file, "w", encoding="utf-8") as f:
            json.dump(unique_ids, f, ensure_ascii=False, indent=2)
        logger.info("Database update complete.")
    background_tasks.add_task(update_task)
    return {"message": "Update task scheduled."}

# --- アプリ起動 ---
if __name__ == "__main__":
    uvicorn.run("ultimate_mygpt:app", host="0.0.0.0", port=8000, reload=True)