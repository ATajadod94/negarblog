#!/usr/bin/env python3
"""
Fetch a Google Scholar profile via SerpAPI and dump publications to _data/scholar.yml
"""

import os, sys, yaml, datetime, pathlib, logging
from scholarly import scholarly, ProxyGenerator
# fake-useragent now optional; comment out if not installed
try:
    from fake_useragent import UserAgent
    RANDOM_UA = True
except ImportError:
    RANDOM_UA = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def init_gateway():
    """Prefer SerpAPI gateway; fallback to direct."""
    pg = ProxyGenerator()
    api_key = os.getenv("SERPAPI_KEY")
    if api_key and pg.SerpApiGateway(api_key):
        scholarly.use_proxy(pg)
        logging.info("Using SerpAPI gateway.")
    else:
        logging.warning("No SERPAPI_KEY provided or gateway init failed – fetching directly.")
    # Optional: random UA (works only if fake_useragent present)
    if RANDOM_UA:
        scholarly._session.headers.update({"User-Agent": UserAgent().random})
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
        except Exception:
            continue
    return pubs

def main(user_id: str):
    init_gateway()
    pubs = fetch_pubs(user_id)
    if not pubs:
        logging.error("No publications fetched – exiting without update")
        sys.exit(0)

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
