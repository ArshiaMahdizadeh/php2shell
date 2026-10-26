@echo off
setlocal
set "SELF=%~dp0"
set "PY=%SELF%.venv\Scripts\python.exe"

if not exist "%PY%" (
    where python >nul 2>nul
    if errorlevel 1 (
        echo php2shell: python not found in PATH
        exit /b 1
    )
    set "PY=python"
)

cd /d "%SELF%"
"%PY%" -m php2shell %*