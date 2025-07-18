@echo off
:: Claude Notifier - One-Click Launcher
:: Just double-click to start everything in background!

echo Starting Claude Notifier...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python first.
    pause
    exit /b 1
)

:: Install dependencies silently if needed
echo Checking dependencies...
pip show pillow >nul 2>&1 || pip install pillow --quiet
pip show pystray >nul 2>&1 || pip install pystray --quiet

:: Kill any existing tray instances
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq claude_status*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq claude_status*" >nul 2>&1

:: Start the tray app in background
echo Starting system tray icon...
cd /d "%~dp0tray"
start "" /B pythonw.exe 1EXEC_claude_tray.py

:: Brief message and auto-close
echo.
echo ===================================
echo Claude Notifier Started!
echo ===================================
echo.
echo - Look for the status icon in system tray
echo - Green = Ready, Yellow = Working
echo - You'll hear a beep when Claude is done
echo.
echo This window will close in 3 seconds...
timeout /t 3 /nobreak >nul

exit