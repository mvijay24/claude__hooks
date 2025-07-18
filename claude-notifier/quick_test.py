#!/usr/bin/env python3
"""Quick test to verify tray status changes"""

import socket
import time

def send_status(status):
    """Send status to tray app"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", 12345))
            s.send(status.encode())
            return True
    except Exception as e:
        print(f"Failed to send status: {e}")
        return False

print("Testing tray icon status changes...")
print("Watch the system tray icon - it should change colors")
print()

# Test sequence
if send_status("working"):
    print("✓ Set to WORKING (yellow/flashing)")
    time.sleep(3)
    
    if send_status("standby"):
        print("✓ Set to STANDBY (green)")
        print("\nTray communication is working correctly!")
    else:
        print("✗ Failed to set standby status")
else:
    print("✗ Tray app not running or not responding")
    print("Please start the notifier first: 1EXEC_START_NOTIFIER.bat")