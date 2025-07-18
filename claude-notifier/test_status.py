#!/usr/bin/env python3
"""Test script to manually send status updates to the tray"""

import socket
import time
import sys

def send_status(status):
    """Send status to tray app"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("127.0.0.1", 12345))
            s.send(status.encode())
            print(f"Sent status: {status}")
    except Exception as e:
        print(f"Failed to send status: {e}")

if __name__ == "__main__":
    print("Testing tray status updates...")
    print("Make sure the tray app is running!")
    print()
    
    while True:
        print("1. Set status to WORKING (yellow)")
        print("2. Set status to STANDBY (green)")
        print("3. Exit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            send_status("working")
        elif choice == "2":
            send_status("standby")
        elif choice == "3":
            break
        else:
            print("Invalid choice")