@echo off
echo Testing sound notification...
echo.
echo Sending working status...
powershell.exe -ExecutionPolicy Bypass -File "C:\ChromeExtensions\Claude             hooks\claude-notifier\powershell_bridge.ps1" -Status "working"
timeout /t 2 /nobreak > nul
echo.
echo Sending standby status (should play sound)...
powershell.exe -ExecutionPolicy Bypass -File "C:\ChromeExtensions\Claude             hooks\claude-notifier\powershell_bridge.ps1" -Status "standby"
echo.
echo Test complete!