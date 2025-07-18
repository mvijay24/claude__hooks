# Claude Code Notifier - Setup Guide

## What This Does
- **Green breathing icon** = Claude is ready
- **Yellow breathing icon** = Claude is working
- Instant visual feedback when you send a message
- Auto-switches back to green when Claude finishes

## Installation

### 1. Start Tray App
Double-click `1EXEC_START_NOTIFIER.bat` - icon will appear in system tray

### 2. Configure Claude Code Hooks
Hooks are already configured in:
- `~/.claude/settings.json`
- `~/.claude_code_settings.json`
- Repository's `claude_code_settings.json`

### 3. IMPORTANT: Restart Claude Code
**You MUST restart Claude Code after hook configuration changes:**
1. Close Claude Code completely (Alt+F4 or X button)
2. Wait 5 seconds
3. Open Claude Code again

## How It Works

### Hooks Fire On:
- **UserPromptSubmit** → Yellow (when you send message)
- **PreToolUse** → Yellow (when Claude uses tools)
- **Stop** → Green (when Claude finishes)

### Technical Details
- Uses PowerShell bridge for WSL→Windows communication
- Tray app listens on port 12345
- Smooth breathing animation (15 frames/cycle)
- Instant response (<0.5 seconds)

## Troubleshooting

### Icon Stuck on Yellow/Green
1. Force green: `powershell.exe -Command "echo standby | nc 127.0.0.1 12345"`
2. Restart tray app: Kill pythonw.exe, run `1EXEC_START_NOTIFIER.bat`

### Hooks Not Firing
1. Check logs: `tail -f hooks/events.log`
2. **RESTART CLAUDE CODE** - hooks don't hot-reload
3. Verify settings have UserPromptSubmit hook

### Common Issues
- **"Invalid settings files"** → Fixed with correct hook structure
- **No color change** → Claude Code needs restart to load new hooks
- **Stuck on yellow** → Stop event not firing, use failsafe

## Test Commands
```bash
# Force yellow
powershell.exe -ExecutionPolicy Bypass -File "C:\ChromeExtensions\Claude             hooks\claude-notifier\powershell_bridge.ps1" -Status "working"

# Force green  
powershell.exe -ExecutionPolicy Bypass -File "C:\ChromeExtensions\Claude             hooks\claude-notifier\powershell_bridge.ps1" -Status "standby"
```

## Final Notes
- Hooks configuration changes require Claude Code restart
- Tray app can run before or after Claude Code starts
- All hooks fire instantly (<0.5 seconds)
- Breathing animation is smooth and non-intrusive