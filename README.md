# php2shell

**CLI exposure scanner for CVE-2026-109618 and CVE-2026-109619**

`php2shell` is a command-line tool for checking PHP applications for potential exposure to the vulnerabilities referenced below. Use it only on systems you own or are explicitly authorized to assess.

- **Reference:** [Palo Alto Networks Unit 42 advisory](https://unit42.paloaltonetworks.com/cve-2026-109618-cve-2026-109619/)
- **Interface:** Command line only
- **Packaging:** Clone the repository and install its dependencies; no PyPI package or library-import workflow is assumed

> **Authorization requirement:** Only scan targets for which you have explicit permission. Start with safe checks and review the methodology before testing production systems.

## Installation

### Windows (PowerShell)

```powershell
git clone https://github.com/ArshiaMahdizadeh/php2shell.git
Set-Location php2shell
.\install.ps1
```

### Linux / macOS (Bash)

```bash
git clone https://github.com/ArshiaMahdizadeh/php2shell.git
cd php2shell
bash install.sh
```

### Manual installation

Create a virtual environment and install the base dependencies:

```bash
python3 -m venv .venv

# Linux / macOS
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m php2shell --help
```

On Windows, use the virtual environment's Windows paths instead:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m php2shell --help
```

### Docker

Build the image:

```bash
docker build -t php2shell .
```

Run a safe scan against a list of authorized targets:

```bash
docker run --rm \
  -v "$PWD/targets.txt:/work/targets.txt:ro" \
  php2shell scan /work/targets.txt --safe
```

`targets.txt` should contain one authorized target per line, in the format expected by the scanner.

## Usage

Display the available commands and options:

```bash
python -m php2shell --help
```

Run a safe batch scan:

```bash
python -m php2shell scan targets.txt --safe
```

Verify a single authorized target:

```bash
python -m php2shell verify https://target.example
```

Write scan output to a dedicated report directory, if supported by the installed version:

```bash
python -m php2shell scan targets.txt --safe --out reports/run-01
```

The `php2shell` and `php2shell.cmd` wrappers may also be used after installation where available.

## Command overview

| Command | Purpose | Expected output |
|---|---|---|
| `scan` | Run checks against a list of targets | HTML report or configured report output |
| `verify` | Check one target | JSON on standard output |

Consult the tool's `--help` output and methodology documentation for the exact options supported by your checkout.

## Repository layout

```text
php2shell/
├── php2shell/
│   ├── cli.py             # CLI entry point
│   ├── scanner.py         # Scan orchestration
│   ├── fingerprinter.py   # PHP version / SAPI fingerprinting
│   ├── ratelimit.py       # Request rate limiting
│   ├── report.py          # Report generation
│   ├── evidence.py        # Evidence handling
│   ├── config.py          # Configuration
│   └── triggers/          # Vulnerability checks
├── tests/
├── docs/
│   └── methodology.md
├── requirements.txt
├── install.sh
├── install.ps1
├── php2shell
├── php2shell.cmd
├── Dockerfile
└── docker-compose.yml
```

## Execution permissions

On Linux and macOS, add executable permissions to shell scripts before running them directly:

```bash
chmod +x install.sh
chmod +x php2shell
```

On Windows, `.ps1` and `.cmd` files do not use Unix permission bits. PowerShell execution policy may affect `.ps1` scripts; `.cmd` files can be run from Command Prompt or PowerShell.

## Responsible use

- Scan only systems you own or have written authorization to test.
- Prefer safe checks and use rate limits appropriate to the target environment.
- Avoid testing production systems without an approved scope and maintenance plan.
- Protect scan reports because they may contain sensitive host and configuration details.
- Follow applicable laws, contracts, and your organization's vulnerability-disclosure process.

Unauthorized access to computer systems may be a crime in many jurisdictions.

## License

MIT License. The software is provided **without warranty**. Review the repository's license file for the complete license terms.
