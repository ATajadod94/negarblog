#!/usr/bin/env python3
"""
Fetch a Google Scholar profile and dump the publications as YAML for Jekyll.
Requires: pip install scholarly pyyaml
"""

import sys, yaml, datetime
from scholarly import scholarly   # unofficial, but works for public profiles

USER_ID = sys.argv[1]             # Google Scholar user ID passed by workflow
MAX_PUBS = 100                    # stop after N items

def main():
    author = scholarly.search_author_id(USER_ID)
    author = scholarly.fill(author, sections=['publications'])
    pubs = []

    for pub in author['publications'][:MAX_PUBS]:
        filled = scholarly.fill(pub)
        bib = filled['bib']
        pubs.append({
            'title':  bib.get('title'),
            'year':   bib.get('pub_year'),
            'venue':  bib.get('venue'),
            'citations': filled.get('num_citations', 0),
            'link':   filled.get('eprint_url') or filled.get('pub_url')
        })

    out = {
        'updated': datetime.date.today().isoformat(),
        'papers':  pubs
    }
    with open('_data/scholar.yml', 'w', encoding='utf-8') as fh:
        yaml.dump(out, fh, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()
