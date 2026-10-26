# Python 3.11 · stealth core — always available
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field

import httpx

from .ua import UA_POOL


@dataclass
class Stealth:
    tor: bool = False
    proxy: str | None = None
    ua_pool: list[str] = field(default_factory=lambda: list(UA_POOL))
    jitter_min_ms: int = 200
    jitter_max_ms: int = 1800
    verify_tls: bool = False

    def client(self) -> httpx.AsyncClient:
        proxies = None
        if self.tor:
            proxies = "socks5://127.0.0.1:9050"
        elif self.proxy:
            proxies = self.proxy
        return httpx.AsyncClient(
            verify=self.verify_tls,
            proxy=proxies,
            follow_redirects=True,
            timeout=20.0,
            headers={"User-Agent": random.choice(self.ua_pool)},
        )

    async def jitter(self) -> None:
        await asyncio.sleep(random.uniform(self.jitter_min_ms, self.jitter_max_ms) / 1000.0)

    def rotate(self, client: httpx.AsyncClient) -> None:
        client.headers["User-Agent"] = random.choice(self.ua_pool)