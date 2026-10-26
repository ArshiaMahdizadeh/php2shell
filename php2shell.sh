#!/usr/bin/env bash
set -euo pipefail

SELF="$(readlink -f "${BASH_SOURCE[0]}")"
ROOT="$(cd "$(dirname "${SELF}")" && pwd)"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
    PY="${ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null; then
    PY="$(command -v python3)"
else
    echo "php2shell: no python3 found" >&2
    exit 1
fi

cd "${ROOT}"
exec "${PY}" -m php2shell "$@"