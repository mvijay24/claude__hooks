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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", TRAY_PORT))
            s.send(status.encode())
            log_event({"action": "tray_update"}, f"Status sent: {status}", "INFO")
    except (ConnectionError, TimeoutError, OSError) as e:
        log_event({"action": "tray_update"}, f"Failed to send status: {e}", "ERROR")
        # Try to start tray if not running
        import subprocess
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect(("127.0.0.1", TRAY_PORT))
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
        
        # Update tray status based on events
        if event_name in ["PreToolUse", "ToolUse", "SubagentStart"]:
            # Claude is starting to work
            log_event(input_data, f"Setting status to WORKING for event: {event_name}", "INFO")
            send_status_to_tray(STATUS_WORKING)
            
        elif event_name in ["Stop", "SubagentStop", "Notification", "PostToolUse"]:
            # Claude is done, waiting for input
            log_event(input_data, f"Setting status to STANDBY for event: {event_name}", "INFO")
            send_status_to_tray(STATUS_STANDBY)
        
        # Always exit successfully
        sys.exit(0)
        
    except Exception as e:
        log_event({"error": str(e)}, f"Hook handler error: {e}", "ERROR")
        print(f"Hook handler error: {e}", file=sys.stderr)
        sys.exit(0)  # Still exit with 0 to not interrupt Claude

if __name__ == "__main__":
    main()