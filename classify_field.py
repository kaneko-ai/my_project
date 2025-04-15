# classify_field.py
# 学習済みモデルを読み込んで、分野を自動判定する関数

import joblib

# 1. モデルの読み込み（前に作った .joblib ファイル）
model = joblib.load("models/field_classifier.joblib")

# 2. 自動分類する関数
def classify_field(title: str, abstract: str) -> str:
    text = (title + " " + abstract).lower()  # タイトルと要約を合体して小文字に
    return model.predict([text])[0]  # 1つの予測結果を返す
