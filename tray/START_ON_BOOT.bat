@echo off
:: Add Claude Notifier to Windows startup

echo Adding Claude Notifier to Windows startup...

:: Create startup shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Claude Notifier.lnk'); $Shortcut.TargetPath = '%~dp0..\1EXEC_CLAUDE_NOTIFIER.exe.bat'; $Shortcut.WorkingDirectory = '%~dp0..'; $Shortcut.IconLocation = 'pythonw.exe'; $Shortcut.Description = 'Claude Status Notifier'; $Shortcut.Save()"

echo.
echo Claude Notifier will now start automatically with Windows!
echo.
pause