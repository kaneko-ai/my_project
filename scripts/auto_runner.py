#!/usr/bin/env python3
# auto_runner.py

import sys
import datetime
from scripts import downloader

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/var/log/auto_runner.log", "a") as f:
        f.write(f"[{now}] {msg}\n")

try:
    log("=== 自動取得開始 ===")
    downloader.download_papers("machine learning")  # 🔁 キーワード変更OK
    log("=== 自動取得完了 ===\n")
except Exception as e:
    log(f"エラー発生: {str(e)}\n")
    sys.exit(1)
