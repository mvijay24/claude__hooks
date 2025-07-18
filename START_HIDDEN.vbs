' Claude Notifier Silent Launcher
' Double-click this file to start without any window

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get current directory
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Run the batch file completely hidden
WshShell.Run chr(34) & strPath & "\1EXEC_START_NOTIFIER.bat" & chr(34), 0, False

' Show a brief notification
WshShell.Popup "Claude Notifier started in system tray!", 2, "Claude Notifier", 64