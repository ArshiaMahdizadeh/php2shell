# Python 3.11 · passive PHP / SAPI fingerprint
from __future__ import annotations

import re
from dataclasses import dataclass

import httpx


@dataclass
class Fingerprint:
    php_version: str | None = None
    sapi: str | None = None
    version_confidence: float = 0.0
    evidence: dict | None = None


HEADER_KEYS = ("x-powered-by", "server")
VERSION_RE = re.compile(r"PHP/(\d+\.\d+\.\d+)", re.IGNORECASE)


async def fingerprint(client: httpx.AsyncClient, url: str) -> Fingerprint:
    evidence: dict = {"headers": {}}
    try:
        r = await client.get(url, timeout=10.0)
        for k in HEADER_KEYS:
            v = r.headers.get(k)
            if v:
                evidence["headers"][k] = v
    except httpx.HTTPError as e:
        return Fingerprint(evidence={"error": type(e).__name__})

    fp = Fingerprint(evidence=evidence)
    for v in evidence["headers"].values():
        m = VERSION_RE.search(v)
        if m:
            fp.php_version = m.group(1)
            fp.version_confidence = 0.9
            break

    server = evidence["headers"].get("server", "").lower()
    if "php-fpm" in server or re.search(r"php/\d", server):
        fp.sapi = "fpm"
    elif "apache" in server and fp.php_version:
        fp.sapi = "mod_php"
    elif "php-cgi" in server:
        fp.sapi = "cgi"

    return fp