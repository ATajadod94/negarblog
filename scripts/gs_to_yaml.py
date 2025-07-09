#!/usr/bin/env python3
"""
Pull Negar's Google Scholar publications and dump them to _data/scholar.yml.
Handles Google's occasional blocks and wrong author IDs gracefully.

Requires:
  pip install scholarly==1.7.11 pyyaml fake-useragent
"""

import sys, yaml, datetime, pathlib, random, logging
from scholarly import scholarly, ProxyGenerator
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def init_proxy():
    """Turn on Scholarly's free_proxy (rotates public proxies) and random UA."""
    pg = ProxyGenerator()
    if pg.FreeProxies():
        scholarly.use_proxy(pg)
        logging.info("Using free proxy pool.")
    try:
        ua = UserAgent().random
        scholarly.set_timeout(10)
        scholarly.set_user_agent(ua)
    except Exception:
        pass

def fetch_pubs(user_id: str, max_pubs: int = 100):
    """Return a list of publication dicts or None if profile not found."""
    try:
        author = scholarly.search_author_id(user_id)
        if not author:
            logging.error("No author found for ID %s", user_id)
            return None
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        logging.error("Failed to fetch profile: %s", e)
        return None

    pubs = []
    for pub in author.get("publications", [])[:max_pubs]:
        try:
            filled = scholarly.fill(pub)
            bib = filled["bib"]
            pubs.append(
                {
                    "title": bib.get("title"),
                    "year": bib.get("pub_year"),
                    "venue": bib.get("venue"),
                    "citations": filled.get("num_citations", 0),
                    "link": filled.get("eprint_url") or filled.get("pub_url"),
                }
            )
        except Exception:
            continue
    return pubs

def main(user_id: str):
    init_proxy()
    pubs = fetch_pubs(user_id)
    if pubs is None:
        logging.error("Exiting without updating _data/scholar.yml")
        sys.exit(0)  # graceful: workflow will continue, commit step will noop

    out = {
        "updated": datetime.date.today().isoformat(),
        "papers": pubs,
    }
    pathlib.Path("_data").mkdir(exist_ok=True)
    with open("_data/scholar.yml", "w", encoding="utf-8") as fh:
        yaml.dump(out, fh, allow_unicode=True, sort_keys=False)
    logging.info("Wrote %d papers to _data/scholar.yml", len(pubs))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gs_to_yaml.py <SCHOLAR_USER_ID>")
        sys.exit(1)
    main(sys.argv[1])
