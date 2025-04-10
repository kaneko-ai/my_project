from transformers import pipeline

qa_generator = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def generate_qna(text):
    # シンプルな質問を生成（本来はLLM推奨）
    questions = [
        "この記事の主題は何ですか？",
        "どんな治療法について述べていますか？"
    ]
    qa_pairs = []
    for q in questions:
        result = qa_generator(question=q, context=text)
        qa_pairs.append((q, result["answer"]))
    return qa_pairs
