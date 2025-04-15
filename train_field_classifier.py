import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# 1. CSVからデータ読み込み
df = pd.read_csv("data/field_train.csv")

# 2. タイトルと要約を合体
X = (df["title"] + " " + df["abstract"]).fillna("")
y = df["field"]  # 分野ラベル

# 3. 機械学習モデル作成
pipeline = Pipeline([
    ("vectorizer", TfidfVectorizer(max_features=1000)),
    ("classifier", LogisticRegression(max_iter=1000))
])

# 4. 学習させる
pipeline.fit(X, y)

# 5. モデル保存
joblib.dump(pipeline, "models/field_classifier.joblib")
print("✅ 学習済みモデルを保存しました")
