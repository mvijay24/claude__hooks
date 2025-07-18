@echo off
echo Creating Windows startup shortcut for Claude Notifier...

:: Get the startup folder path
set "startup=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Create the shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%startup%\Claude Notifier.lnk'); $Shortcut.TargetPath = '%~dp01EXEC_START_NOTIFIER.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%~dp0tray\icon_standby.ico'; $Shortcut.Description = 'Claude Code Notifier - Visual feedback for Claude activity'; $Shortcut.Save()"

if exist "%startup%\Claude Notifier.lnk" (
    echo.
    echo SUCCESS! Claude Notifier will now start automatically with Windows.
    echo Shortcut created at: %startup%\Claude Notifier.lnk
    echo.
    echo To remove auto-start: Delete the shortcut from your Startup folder
    echo Location: %startup%
) else (
    echo.
    echo ERROR: Failed to create startup shortcut.
    echo Please run this script as Administrator if needed.
)

echo.
pause