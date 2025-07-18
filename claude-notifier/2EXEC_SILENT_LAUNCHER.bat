@echo off
:: Ultra Simple Claude Notifier Launcher
:: Just double-click and forget!

:: Start in background using VBScript (no window)
start "" /B wscript.exe "%~dp0START_HIDDEN.vbs"
exit