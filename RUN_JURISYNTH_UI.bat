@echo off
setlocal
where pwsh.exe >nul 2>nul
if errorlevel 1 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_JURISYNTH_UI.ps1"
) else (
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_JURISYNTH_UI.ps1"
)
if errorlevel 1 (
    echo.
    echo Jurisynth could not start. Read the message above; no eval was launched.
    pause
)
endlocal
