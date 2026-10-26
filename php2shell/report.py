# Python 3.11 · HTML report
from __future__ import annotations

from pathlib import Path

from jinja2 import Template

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>php2shell report</title>
<style>
:root { color-scheme: dark; }
body { font-family: ui-monospace, Menlo, monospace; background:#0b0d10; color:#d5dae0; padding:32px; }
h1 { font-size:22px; } .host { border:1px solid #1e2530; padding:12px; margin:8px 0; border-radius:6px; }
.tag { display:inline-block; padding:2px 8px; border-radius:4px; font-size:12px; margin-right:6px; }
.hit { background:#7a1f1f; color:#ffd7d7; } .sus { background:#7a5c1f; color:#ffe8b8; }
.ok { background:#1f4a30; color:#b8f0d0; } small { color:#7d8794; }
</style></head><body>
<h1>php2shell · scan report</h1>
<p><small>{{ count }} targets · CVE-2026-109618 / CVE-2026-109619</small></p>
{% for r in results %}<div class="host">
<strong>{{ r.url }}</strong><br>
{% if r.confident %}<span class="tag hit">CONFIDENT {{ r.confident|join(', ') }}</span>{% endif %}
{% if r.suspected %}<span class="tag sus">SUSPECTED {{ r.suspected|join(', ') }}</span>{% endif %}
{% if not r.confident and not r.suspected %}<span class="tag ok">CLEAN</span>{% endif %}
<small>php={{ r.php_version or '?' }} sapi={{ r.sapi or '?' }}</small>
</div>{% endfor %}</body></html>"""


def write_html(results, path: Path) -> None:
    path.write_text(Template(TEMPLATE).render(results=results, count=len(results)), encoding="utf-8")