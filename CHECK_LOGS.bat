@echo off
echo Claude Notifier Log Viewer
echo =========================
echo.

set LOG_FILE="C:\ChromeExtensions\Claude             hooks\claude-notifier\hooks\events.log"

if exist %LOG_FILE% (
    echo Recent log entries:
    echo -------------------
    powershell -Command "Get-Content %LOG_FILE% -Tail 20"
    echo.
    echo -------------------
    echo Full log file: %LOG_FILE%
) else (
    echo No log file found yet.
    echo Run some Claude Code commands to generate logs.
)

echo.
pause