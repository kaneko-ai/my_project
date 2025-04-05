import argparse
import os

def fetch_and_process():
    # ※ここに実際のPubMed APIを呼び出すコードや、論文データを整形する処理を実装
    print("PubMedから論文を取得し、整形処理を実行中...")
    
    # 処理結果を output ディレクトリに保存する例
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)  # フォルダがなければ作成する
    output_file = os.path.join(output_dir, "processed_data.txt")
    
    # ここではサンプルとしてテキストを書き込む
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ここに整形済み論文のデータが入ります。")
    
    print("処理完了。成果物は", output_file, "に保存されました。")

def main(mode):
    if mode == "production":
        print("【本番モード】処理を開始します。")
        fetch_and_process()
    else:
        print("【開発モード】デバッグ用の処理を実行します。")
        # デバッグ用の処理（例：簡単なメッセージの表示など）
        print("Hello, World!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PubMed 論文取得＆整形処理")
    parser.add_argument('--mode', type=str, default='development', help='実行モード (production または development)')
    args = parser.parse_args()
    main(args.mode)
