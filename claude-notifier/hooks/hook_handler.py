#!/usr/bin/env python3
"""
Claude Code Hook Handler with Sound and Tray Integration
========================================================
Plays a sound when Claude is done and updates system tray status
"""

import sys
import json
import subprocess
from pathlib import Path
import socket
import time

# Configuration
TRAY_PORT = 12345  # Port for communicating with tray app
STATUS_WORKING = "working"
STATUS_STANDBY = "standby"
LOGGING_ENABLED = True  # Default, will be updated from tray app

def send_status_to_tray(status):
    """Send status update to the system tray application"""
    try:
        # Use PowerShell to bridge WSL to Windows connection
        ps_script = Path(__file__).parent.parent / "powershell_bridge.ps1"
        subprocess.run([
            "powershell.exe", "-ExecutionPolicy", "Bypass", "-File", 
            str(ps_script).replace("/mnt/c", "C:").replace("/", "\\"),
            "-Status", status
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_event({"action": "tray_update"}, f"Status sent via PowerShell: {status}", "INFO")
    except Exception as e:
        log_event({"action": "tray_update"}, f"Failed to send status: {e}", "ERROR")
        # Try to start tray if not running
        try:
            subprocess.Popen(["pythonw", "C:/ChromeExtensions/Claude             hooks/claude-notifier/tray/claude_tray.py"], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_event({"action": "tray_start"}, "Attempted to start tray app", "INFO")
        except:
            pass

def play_sound(sound_file):
    """Play a sound file using Windows Media Player via PowerShell"""
    try:
        log_event({"action": "play_sound"}, f"Attempting to play: {sound_file}", "DEBUG")
        # Use PowerShell to play sound
        ps_command = f"""
        Add-Type -AssemblyName System.Media
        $player = New-Object System.Media.SoundPlayer
        $player.SoundLocation = '{sound_file}'
        $player.PlaySync()
        """
        
        subprocess.Popen(
            ["powershell.exe", "-Command", ps_command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log_event({"action": "play_sound"}, "Sound command sent", "INFO")
    except Exception as e:
        log_event({"action": "play_sound"}, f"Error: {e}", "ERROR")
        print(f"Error playing sound: {e}", file=sys.stderr)

def get_logging_config():
    """Get logging configuration from tray app"""
    global LOGGING_ENABLED
    try:
        # Get Windows host IP for WSL
        import subprocess
        result = subprocess.run(['cat', '/etc/resolv.conf'], capture_output=True, text=True)
        windows_ip = "127.0.0.1"  # fallback
        for line in result.stdout.split('\n'):
            if 'nameserver' in line:
                windows_ip = line.split()[1]
                break
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((windows_ip, TRAY_PORT))
            s.send(b"get_config")
            data = s.recv(1024).decode()
            config = json.loads(data)
            LOGGING_ENABLED = config.get('logging_enabled', True)
    except:
        # If can't connect, keep default
        pass

def log_event(event_data, message="", level="INFO"):
    """Log events for debugging with more details"""
    if not LOGGING_ENABLED:
        return
    try:
        log_path = Path(__file__).parent / "events.log"
        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            event_name = event_data.get("hook_event_name", "Unknown") if isinstance(event_data, dict) else str(event_data)
            tool_name = event_data.get("tool_name", "") if isinstance(event_data, dict) else ""
            
            log_entry = f"{timestamp} [{level}] Event: {event_name}"
            if tool_name:
                log_entry += f", Tool: {tool_name}"
            if message:
                log_entry += f" - {message}"
            
            f.write(f"{log_entry}\n")
            f.flush()  # Ensure immediate write
    except Exception as e:
        print(f"Logging error: {e}", file=sys.stderr)

def main():
    try:
        # Get logging config from tray app
        get_logging_config()
        
        # Read event data from Claude
        input_data = json.load(sys.stdin)
        log_event(input_data)
        
        event_name = input_data.get("hook_event_name", "")
        tool_name = input_data.get("tool_name", "")
        
        # Log all events for debugging
        log_event(input_data, f"Received event: {event_name}, Tool: {tool_name}", "INFO")
        
        # INSTANT YELLOW - NO DELAY, NO BULLSHIT
        if event_name == "UserPromptSubmit":
            # IMMEDIATELY turn yellow when user sends message
            log_event(input_data, "INSTANT YELLOW on UserPromptSubmit!", "INFO")
            send_status_to_tray(STATUS_WORKING)
            # That's it. No checking, no waiting, just YELLOW NOW!
        
        # Update tray status based on OTHER events (not UserPromptSubmit - already handled above)
        elif event_name in ["PreToolUse", "ToolUse", "SubagentStart"]:
            # Claude is starting to work
            log_event(input_data, f"Setting status to WORKING for event: {event_name}", "INFO")
            send_status_to_tray(STATUS_WORKING)
            
        elif event_name in ["Stop", "SubagentStop", "Notification"]:
            # Claude is done, waiting for input
            log_event(input_data, f"Setting status to STANDBY for event: {event_name}", "INFO")
            send_status_to_tray(STATUS_STANDBY)
            
        elif event_name == "PostToolUse":
            # Keep working status during PostToolUse (more tools might follow)
            log_event(input_data, f"Keeping WORKING status for event: {event_name}", "INFO")
        
        # Always exit successfully
        sys.exit(0)
        
    except Exception as e:
        log_event({"error": str(e)}, f"Hook handler error: {e}", "ERROR")
        print(f"Hook handler error: {e}", file=sys.stderr)
        sys.exit(0)  # Still exit with 0 to not interrupt Claude

if __name__ == "__main__":
    main()