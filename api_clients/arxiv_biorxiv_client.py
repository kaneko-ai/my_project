import requests
import xml.etree.ElementTree as ET

def fetch_arxiv_articles(query="natural language processing", max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"arXiv API error: {response.status_code}")

    root = ET.fromstring(response.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    results = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        link = entry.find("atom:id", ns).text.strip()
        results.append({"title": title, "url": link})

    return results
