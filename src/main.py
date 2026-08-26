import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin
import time
from pydantic import BaseModel, HttpUrl
import re
import json


USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/yourusername/your-repo)"
TIMEOUT = 10
CACHE_DIR = "cache"


class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_gbp: float
    price_text: str
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: str
    fetched_at: str


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


def get_soup(html):
    return BeautifulSoup(html, "html.parser")


def discover_book_urls():
    base_url = "https://books.toscrape.com/catalogue/page-1.html"
    all_urls = []
    page_num = 1
    current_url = base_url

    while True:
        cache_name = f"catalogue-page-{page_num}.html"
        html = fetch_page(current_url, cache_name)
        soup = get_soup(html)

        for a in soup.select("h3 a"):
            book_url = urljoin(current_url, a["href"])
            all_urls.append(book_url)

        next_link = soup.select_one("li.next a")
        if not next_link:
            break

        if page_num > 1:
            time.sleep(0.5)  # politeness delay between real page requests

        current_url = urljoin(current_url, next_link["href"])
        page_num += 1

    # removes duplicates, keeps order
    unique_urls = list(dict.fromkeys(all_urls))
    print(
        f"catalogue_pages={page_num} discovered={len(all_urls)} unique_urls={len(unique_urls)}")
    return unique_urls


def extract_book(url, source_page):
    cache_name = url.split("/catalogue/")[-1].replace("/", "_")
    html = fetch_page(url, cache_name)
    soup = get_soup(html)

    product_area = soup.select_one("div.product_main")
    title = product_area.select_one("h1").text.strip()

    price_text = soup.select_one("p.price_color").text.strip()
    availability_text = soup.select_one("p.availability").text.strip()

    rating_tag = soup.select_one("p.star-rating")
    rating_text = rating_tag["class"][1] if rating_tag else None

    desc_tag = soup.select_one("#product_description ~ p")
    description = desc_tag.text.strip() if desc_tag else None

    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def normalize_and_validate(raw_records):
    valid, errors = [], []
    for r in raw_records:
        try:
            price_num = float(re.sub(r"[^\d.]", "", r["price_text"]))
            record = Book(
                title=r["title"],
                product_url=r["product_url"],
                price_gbp=price_num,
                price_text=r["price_text"],
                availability_text=r["availability_text"],
                rating_text=r["rating_text"],
                description=r["description"],
                source_page=r["source_page"],
                fetched_at=r["fetched_at"]
            )
            valid.append(record.model_dump(mode="json"))
        except Exception as e:
            errors.append({"record": r, "reason": str(e)})

    # idempotency: dedupe by canonical URL
    seen, deduped = set(), []
    for v in valid:
        if v["product_url"] not in seen:
            seen.add(v["product_url"])
            deduped.append(v)

    os.makedirs("output", exist_ok=True)
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)
    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)

    return deduped, errors


if __name__ == "__main__":
    html = fetch_page(
        "https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
