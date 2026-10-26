
param([switch]$Full)

$ErrorActionPreference = "Stop"
$Here = $PSScriptRoot
$Venv = Join-Path $Here ".venv"
$Py   = Join-Path $Venv "Scripts\python.exe"
$Pip  = Join-Path $Venv "Scripts\pip.exe"

Write-Host "[*] php2shell installer (windows)" -ForegroundColor Cyan
Write-Host "    repo: $Here"
Write-Host "    venv: $Venv"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] python not found in PATH. Install from https://python.org with 'Add to PATH' checked." -ForegroundColor Red
    exit 1
}

python -m venv $Venv
& $Py -m pip install --upgrade pip | Out-Null

Write-Host "[*] installing base requirements"
& $Pip install -r (Join-Path $Here "requirements.txt")

if ($Full) {
    Write-Host "[*] installing extras"
    & $Pip install -r (Join-Path $Here "requirements-extras.txt")
}

$Launcher = Join-Path $Here "php2shell.cmd"
if (Test-Path $Launcher) {
    $userBin = Join-Path $env:USERPROFILE "bin"
    New-Item -ItemType Directory -Force -Path $userBin | Out-Null
    $target = Join-Path $userBin "php2shell.cmd"
    Copy-Item $Launcher $target -Force
    Write-Host "[+] copied launcher to $target"

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$userBin*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$userBin", "User")
        Write-Host "[+] added $userBin to User PATH (restart terminal to pick it up)"
    }
}

Write-Host "[+] done. run: php2shell --help" -ForegroundColor Green