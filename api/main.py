from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from scripts import auto_download_and_save as downloader, history_logger, pdf_summarizer

app = FastAPI(
    title="AI論文処理API",
    description="論文の分類・要約・評価を行うAPIです",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root():
    return {"message": "Welcome to the Paper Downloader API!"}


@app.get("/download_papers")
def download_papers(keyword: str):
    result = downloader.download_papers(keyword)
    return {"result": result}


@app.get("/download_history")
def get_history(keyword: str = None, after: str = None, filename: str = None):
    filters = {
        "keyword": keyword,
        "after": after,
        "filename": filename
    }
    return history_logger.read_log(filters)


@app.get("/download_history/html", response_class=HTMLResponse)
def get_history_html(request: Request, keyword: str = None, after: str = None, filename: str = None):
    filters = {
        "keyword": keyword,
        "after": after,
        "filename": filename
    }
    entries = history_logger.read_log(filters)
    return templates.TemplateResponse("history.html", {"request": request, "entries": entries})


@app.get("/summarize_paper")
def summarize_paper(filename: str):
    summary = pdf_summarizer.summarize_pdf(filename)
    return {"summary": summary}
