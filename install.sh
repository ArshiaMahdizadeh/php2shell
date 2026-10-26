#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${HERE}/.venv"
LAUNCHER="${HOME}/.local/bin/php2shell"

echo "[*] php2shell installer"
echo "    repo: ${HERE}"
echo "    venv: ${VENV}"
echo "    bin:  ${LAUNCHER}"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[!] python3 not found in PATH" >&2
    exit 1
fi

python3 -m venv "${VENV}"
# shellcheck disable=SC1091
source "${VENV}/bin/activate"

pip install --upgrade pip >/dev/null
pip install -r "${HERE}/requirements.txt"

if [[ "${1:-}" == "--full" ]]; then
    echo "[*] installing extras"
    pip install -r "${HERE}/requirements-extras.txt"
fi

chmod +x "${HERE}/php2shell"

mkdir -p "$(dirname "${LAUNCHER}")"
ln -sf "${HERE}/php2shell" "${LAUNCHER}"
echo "[+] linked ${LAUNCHER}"

case ":${PATH}:" in
    *:"$(dirname "${LAUNCHER}")":*)
        ;;
    *)
        echo "[!] $(dirname "${LAUNCHER}") is not in PATH."
        echo "    Add to your shell rc:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        ;;
esac

echo "[+] done. run: php2shell --help"