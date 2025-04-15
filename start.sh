#!/bin/bash

# Gradio (ポート7860) & FastAPI (ポート8000) を同時起動
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
python app/gradio_arxiv_ui.py
