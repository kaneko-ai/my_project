import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# 読み込み
base = pd.read_csv("data/train.csv")
mis = pd.read_csv("data/misclassified.csv")
df = pd.concat([base, mis])

# 特徴抽出
vectorizer = TfidfVectorizer(max_features=3000)
X = vectorizer.fit_transform(df["summary"])
y = df["label"]

# 学習
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

# 保存
joblib.dump(clf, "models/sklearn_retrained.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

# モデル履歴更新
with open("models/model_history.csv", "a", encoding="utf-8") as f:
    f.write("sklearn_retrained.pkl, retrained after misclassified\n")

print("✅ 再学習完了。新モデル保存済み。")
