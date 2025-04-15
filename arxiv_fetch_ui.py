import streamlit as st

print("✅ Streamlit 起動しました！")  # ターミナルに出るはず
st.title("📄 arXiv論文取得テスト")

try:
    import sys
    import os
    import requests
    import xml.etree.ElementTree as ET
    print("✅ すべてのライブラリがインポートされました！")
except Exception as e:
    st.error(f"モジュール読み込み失敗: {e}")
