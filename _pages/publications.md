---
title: "Publications"
layout: single
permalink: /publications/
---

_Last updated: {{ site.data.scholar.updated }}_

| Year | Title | Venue | Citations |
|------|-------|-------|-----------|
{% for p in site.data.scholar.papers %}
| {{ p.year }} | [{{ p.title }}]({{ p.link }}) | {{ p.venue | xml_escape }} | {{ p.citations }} |
{% endfor %}
