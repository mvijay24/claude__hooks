@echo off
echo Testing tray status updates...
echo.

:: Start tray if not running
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul || (
    echo Starting tray app...
    cd /d "%~dp0"
    start "" /B pythonw.exe tray\claude_tray.py
    timeout /t 2 >nul
)

echo.
echo Testing status changes:
echo.

echo Setting status to WORKING (yellow)...
python test_status.py < nul

pause