# Claude__Hooks 🔔

A notification system for Claude Code that provides audio alerts and visual status indicators when Claude completes tasks.

## Features

- 🔊 **Sound Notifications** - Plays a beep when Claude finishes tasks
- 🟢 **System Tray Status** - Green (ready) / Yellow flashing (working)
- 📝 **Optional Logging** - Toggle logging on/off from tray menu
- 🚀 **One-Click Launch** - Simple executable to start everything

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mvijay24/claude__hooks.git
   cd claude__hooks
   ```

2. **Run the launcher**:
   ```
   1EXEC_CLAUDE_NOTIFIER.exe.bat
   ```

3. **Configure Claude Code**:
   Add to your Claude Code settings (`claude-code settings`):
   ```json
   {
     "hooks": {
       "PreToolUse": "python \"C:\\path\\to\\claude__hooks\\hooks\\hook_handler.py\"",
       "Stop": "python \"C:\\path\\to\\claude__hooks\\hooks\\hook_handler.py\"",
       "SubagentStop": "python \"C:\\path\\to\\claude__hooks\\hooks\\hook_handler.py\"",
       "Notification": "python \"C:\\path\\to\\claude__hooks\\hooks\\hook_handler.py\""
     }
   }
   ```

## Requirements

- Windows OS
- Python 3.x
- Claude Code CLI

## Project Structure

```
claude__hooks/
├── 1EXEC_CLAUDE_NOTIFIER.exe.bat  # Main launcher
├── hooks/
│   └── hook_handler.py            # Hook event processor
├── sounds/
│   └── done.wav                   # Notification sound
└── tray/
    └── 1EXEC_claude_tray.py       # System tray app
```

## System Tray Menu

Right-click the tray icon for:
- **Status** - Shows current Claude status
- **Logging** - Toggle logging on/off
- **Quit** - Exit the application

## Auto-Start

To start with Windows:
```
tray\START_ON_BOOT.bat
```

## Troubleshooting

- **No tray icon?** Check if Python and required packages are installed
- **No sound?** Verify `sounds/done.wav` exists
- **View logs**: Run `CHECK_LOGS.bat`

## License

MIT