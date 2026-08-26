import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/yourusername/your-repo)"
TIMEOUT = 10
CACHE_DIR = "cache"


def fetch_page(url, cache_filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_filename}")
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"size={len(html)} bytes")
        return html

    print(f"FETCH: {url}")
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch {url}: status {response.status_code}")

    html = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"size={len(html)} bytes")
    return html


if __name__ == "__main__":
    html = fetch_page(
        "https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
