@echo off
cd /d "C:\ChromeExtensions\Claude             hooks\claude-notifier\tray"
start "" pythonw claude_tray_with_volume.py
echo Claude notifier started with volume control!
echo Right-click the tray icon to adjust volume (10%, 25%, 50%, 75%, 100%)
timeout /t 3