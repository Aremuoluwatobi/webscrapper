# The Polite Scraper — FlyRank W5·A9

A small, polite scraping pipeline that collects 60 books from Books to Scrape (a public practice sandbox),
turns messy HTML into clean, validated JSON, and survives a broken page without crashing.

## Target classification

- **Site:** books.toscrape.com
- **Purpose:** a public sandbox built specifically for practicing web scraping
- **Scope:** the first 3 catalogue pages, and the 60 book pages linked from them
- **robots.txt result:** no robots.txt file found (404)
- **Why this is appropriate:** the site's own stated purpose is to be scraped for practice, and access here is limited to a small, defined scope

I will not reuse this code on another site without checking its rules and terms first.

## Install

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Run

\`\`\`bash
python src/main.py
\`\`\`

This fetches the catalogue, visits all 60 book pages, validates each record, and writes:
- `output/books.json` — validated records
- `output/errors.json` — records that failed validation, with reasons
- `output/run-report.json` — a summary of the run

## Record schema

Each record in `books.json` has:

| Field | Type | Notes |
|---|---|---|
| title | string | book title |
| product_url | string (URL) | canonical identity of the record |
| price_gbp | number | normalized from price_text, e.g. "£51.77" → 51.77 |
| price_text | string | original price as shown on the page |
| availability_text | string | e.g. "In stock (22 available)" |
| rating_text | string or null | star rating word, e.g. "Three" |
| description | string or null | null when the book has no description on the page |
| source_page | string | catalogue page the book was discovered from |
| fetched_at | string (ISO datetime) | when the page was fetched |

## Politeness rules followed

- Every real request sends an identifying User-Agent: `FlyRankInternshipA9/1.0 (+link-to-repo)`
- A 10-second timeout on every request
- A 0.5s delay between real catalogue page requests
- HTML pages are cached to `cache/` after the first fetch — development reads from cache, not the live site
- Only status 200 responses are treated as successful; anything else is a failed fetch

## Sample run report

\`\`\`json
[paste your actual output/run-report.json contents here]
\`\`\`

## Limitations

- Retry logic is minimal: a single automatic retry only applies to timeouts and 5xx errors; 404s and 403s are not retried by design
- No exponential backoff or Retry-After handling yet — that's covered by next week's assignment (A16)

## Ethics note

This scraper only touches a site built explicitly for scraping practice, at a small, defined scope.
In general: use an official API when one exists, never bypass logins, paywalls, or access blocks, and only
collect the data actually needed for the task.