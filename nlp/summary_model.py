# summary_model.py

from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# ✅ モデルとトークナイザーの初期化
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

def summarize_with_pegasus(text: str, max_length=128, min_length=32) -> str:
    """
    Pegasusモデルを使用してテキストを要約する関数
    """
    # 入力をトークナイズ
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest", max_length=1024)

    # 要約生成
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True,
    )

    # 要約のデコード
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
