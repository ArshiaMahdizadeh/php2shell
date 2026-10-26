# Python 3.11 · tor health check
from __future__ import annotations

import httpx


async def tor_alive(proxy: str = "socks5://127.0.0.1:9050") -> bool:
    try:
        async with httpx.AsyncClient(proxy=proxy, timeout=8.0) as c:
            r = await c.get("https://check.torproject.org/api/ip")
            return bool(r.json().get("IsTor"))
    except httpx.HTTPError:
        return False