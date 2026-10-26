# Python 3.11 · trigger base types
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol

import httpx


@dataclass
class TriggerResult:
    cve: str
    hit: bool
    confidence: float
    evidence: dict = field(default_factory=dict)
    duration_ms: int = 0


class Trigger(Protocol):
    cve: str

    async def run(self, client: httpx.AsyncClient, url: str) -> TriggerResult: ...


async def probe(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    body: bytes | None = None,
    timeout: float = 10.0,
) -> tuple[httpx.Response | None, int, str | None]:
    start = time.perf_counter()
    try:
        r = await client.request(method, url, headers=headers, content=body, timeout=timeout)
        return r, int((time.perf_counter() - start) * 1000), None
    except (httpx.TimeoutException, httpx.TransportError) as e:
        return None, int((time.perf_counter() - start) * 1000), type(e).__name__