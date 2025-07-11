#!/usr/bin/env python3
"""
Fetch Negar's Google Scholar publications through SerpAPI and write _data/scholar.yml
"""

import os
import yaml
from serpapi import GoogleSearch
import datetime

SERPAPI_KEY = os.getenv("SERPAPI_KEY") or "YOUR_SERPAPI_KEY"
AUTHOR_ID = "R_1o4RIAAAAJ"  # Replace with your Scholar user ID

params = {
    "engine": "google_scholar_author",
    "author_id": AUTHOR_ID,
    "api_key": SERPAPI_KEY
}

search = GoogleSearch(params)
results = search.get_dict()

papers = []
for pub in results.get("articles", []):
    papers.append({
        "title": pub.get("title"),
        "year": pub.get("year"),
        "venue": pub.get("publication"),
        "citations": pub.get("cited_by", {}).get("value", 0),
        "link": pub.get("link"),
    })

data = {
    "updated": datetime.date.today().isoformat(),
    "papers": papers
}

os.makedirs("_data", exist_ok=True)
with open("_data/scholar.yml", "w", encoding="utf-8") as fh:
    yaml.dump(data, fh, allow_unicode=True, sort_keys=False)

print(f"Wrote {len(papers)} papers to _data/scholar.yml")
