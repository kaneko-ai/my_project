# nlp/summary_model.py

from transformers import pipeline

# モデルキャッシュ
_summarizers = {}

def summarize_text(text: str, model: str = "default") -> str:
    model_map = {
        "default": "sshleifer/distilbart-cnn-12-6",
        "bart": "facebook/bart-large-cnn",
        "pegasus": "google/pegasus-xsum"
    }

    if model not in model_map:
        model = "default"

    model_name = model_map[model]

    if model_name not in _summarizers:
        _summarizers[model_name] = pipeline("summarization", model=model_name)

    summarizer = _summarizers[model_name]
    result = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return result[0]["summary_text"]
