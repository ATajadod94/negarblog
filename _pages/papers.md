---
title: "Papers"
permalink: /papers/
layout: single
author_profile: true
---

_Last updated: {{ site.data.scholar.updated }}_

<div class="papers-list">
  {% for p in site.data.scholar.papers %}
    <div class="paper-card">
      <h2 class="paper-title">
        {% if p.link %}
          <a href="{{ p.link }}" target="_blank">{{ p.title }}</a>
        {% else %}
          {{ p.title }}
        {% endif %}
      </h2>
      <div class="paper-meta">
        <span class="paper-year">{{ p.year }}</span>
        {% if p.venue %} | <span class="paper-venue">{{ p.venue }}</span>{% endif %}
        {% if p.citations %} | <span class="paper-citations">Citations: {{ p.citations }}</span>{% endif %}
      </div>
    </div>
  {% endfor %}
</div> 