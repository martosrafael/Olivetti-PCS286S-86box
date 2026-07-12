@echo off
setlocal

set "SCRIPT=%~dp0bios_tool.py"

where python >nul 2>nul
if not errorlevel 1 (
    python -V >nul 2>nul
    if not errorlevel 1 (
        python "%SCRIPT%" %*
        exit /b %ERRORLEVEL%
    )
)

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -V >nul 2>nul
    if not errorlevel 1 (
        py -3 "%SCRIPT%" %*
        exit /b %ERRORLEVEL%
    )
)

set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CODEX_PYTHON%" (
    "%CODEX_PYTHON%" "%SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

echo No Python runtime found. Install Python 3 or run this from Codex with the bundled runtime available. 1>&2
exit /b 1
