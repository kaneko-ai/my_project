# app/interactive_search.py

from nlp.vector_db import search_similar

def interactive_query(user_input: str):
    """
    ChatGPT風に自然言語クエリから類似論文を検索・整形して返す
    """
    print(f"\n🔍「{user_input}」について類似論文を検索中...\n")
    results = search_similar(user_input, top_k=5)

    response = "🧠 類似論文トップ5:\n"
    for i, hit in enumerate(results, 1):
        response += f"\n{i}. 『{hit['title']}』\n"
        response += f"   📊 類似スコア: {hit['score']}\n"
        response += f"   📄 要約: {hit['content'][:200]}...\n"
    return response


# 実行例
if __name__ == "__main__":
    user_input = input("💬 聞きたいことをどうぞ：")
    print(interactive_query(user_input))
