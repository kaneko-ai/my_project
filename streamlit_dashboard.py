import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from tools.db import get_tag_statistics, get_year_distribution

st.set_page_config(page_title="論文統計ダッシュボード", layout="wide")

st.title("📊 論文タグ・スコア統計ダッシュボード")

# タグ別件数とスコア
st.subheader("タグ別 論文数・平均スコア")
tag_df = get_tag_statistics()
st.dataframe(tag_df)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(tag_df["タグ"], tag_df["件数"])
ax.set_title("タグ別 論文数")
ax.set_ylabel("件数")
plt.xticks(rotation=45)
st.pyplot(fig)

# 年別件数分布
st.subheader("発表年別 論文数")
year_df = get_year_distribution()
st.dataframe(year_df)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(year_df["年"], year_df["件数"], marker='o')
ax2.set_title("年別 論文数の推移")
ax2.set_ylabel("件数")
st.pyplot(fig2)

st.markdown("---")
st.caption("powered by CodeMaster")
