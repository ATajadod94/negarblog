#!/usr/bin/env python3
"""
Fetch a Google Scholar profile via SerpAPI and dump publications to _data/scholar.yml

Dependencies (install in workflow):
  scholarly==1.7.11
  pyyaml
  fake-useragent
  httpx<0.27     # scholarly still expects httpx 0.26 interface
"""

import os, sys, yaml, datetime, pathlib, logging
from fake_useragent import UserAgent
from scholarly import scholarly, ProxyGenerator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def init_gateway():
    """Configure scholarly to use SerpAPI gateway or fallback to direct."""
    pg = ProxyGenerator()
    api_key = os.getenv("SERPAPI_KEY")
    if api_key and pg.SerpApiGateway(api_key):
        scholarly.use_proxy(pg)
        logging.info("Using SerpAPI gateway.")
    else:
        logging.warning("No SERPAPI_KEY provided or gateway init failed – fetching directly.")
    # Random UA + timeout for politeness
    scholarly.set_user_agent(UserAgent().random)
    scholarly.set_timeout(10)

def fetch_pubs(user_id: str, max_pubs: int = 100):
    author = scholarly.search_author_id(user_id)
    if not author:
        logging.error("Author ID %s not found.", user_id)
        return []
    author = scholarly.fill(author, sections=["publications"])
    pubs = []
    for pub in author.get("publications", [])[:max_pubs]:
        try:
            filled = scholarly.fill(pub)
            bib = filled["bib"]
            pubs.append({
                "title":      bib.get("title"),
                "year":       bib.get("pub_year"),
                "venue":      bib.get("venue"),
                "citations":  filled.get("num_citations", 0),
                "link":       filled.get("eprint_url") or filled.get("pub_url"),
            })
        except Exception as e:
            logging.warning("Skipping a pub: %s", e)
    return pubs

def main(user_id: str):
    init_gateway()
    pubs = fetch_pubs(user_id)
    if not pubs:
        logging.error("No publications fetched – exiting without update")
        sys.exit(0)       # exit 0 so workflow continues but commit step will noop

    data = {
        "updated": datetime.date.today().isoformat(),
        "papers":  pubs,
    }
    pathlib.Path("_data").mkdir(exist_ok=True)
    with open("_data/scholar.yml", "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=False)
    logging.info("Wrote %d publications to _data/scholar.yml", len(pubs))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gs_to_yaml.py <GOOGLE_SCHOLAR_USER_ID>")
        sys.exit(1)
    main(sys.argv[1])
