import json
from pathlib import Path
from datetime import datetime
import os
from PyPDF2 import PdfReader

LOG_FILE = Path("logs/download_log.json")
LOG_FILE.parent.mkdir(exist_ok=True)

def log_download(keyword, filename, url):
    log = read_log()
    file_path = Path("papers") / filename
    size = file_path.stat().st_size if file_path.exists() else None
    pages = None
    try:
        reader = PdfReader(str(file_path))
        pages = len(reader.pages)
    except:
        pass

    log.append({
        "keyword": keyword,
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "file_size": size,
        "pages": pages
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def read_log(filters=None):
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        data = json.load(f)

    if not filters:
        return data

    keyword = filters.get("keyword")
    after = filters.get("after")
    filename = filters.get("filename")

    if after:
        try:
            after_date = datetime.fromisoformat(after)
        except ValueError:
            after_date = None
    else:
        after_date = None

    filtered = []
    for entry in data:
        if keyword and keyword.lower() not in entry.get("keyword", "").lower():
            continue
        if filename and filename.lower() not in entry.get("filename", "").lower():
            continue
        if after_date:
            entry_time = datetime.fromisoformat(entry.get("timestamp"))
            if entry_time < after_date:
                continue
        filtered.append(entry)
    return filtered
