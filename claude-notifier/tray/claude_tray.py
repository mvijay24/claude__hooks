#!/usr/bin/env python3
"""
Claude Status Tray Icon
======================
Shows Claude's working status in the system tray
- Yellow (flashing) = Working
- Green = Standby/Ready
"""

import sys
import socket
import threading
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu

# Configuration
LISTEN_PORT = 12345
ICON_SIZE = 64
CONFIG_FILE = Path(__file__).parent.parent / "config.json"

class ClaudeTrayApp:
    def __init__(self):
        self.status = "standby"
        self.icon = None
        self.running = True
        self.flash_state = False
        self.logging_enabled = True
        self.breathing_phase = 0  # For smooth breathing effect
        
        # Load config
        self.load_config()
        
        # Create icon sets for breathing animation
        self.green_icons = []
        self.yellow_icons = []
        
        # Create gradient of green icons (breathing effect)
        for i in range(8):
            brightness = int(120 + (135 * (i / 7)))  # 120-255
            self.green_icons.append(self.create_icon_image((0, brightness, 0)))
        
        # Create gradient of yellow icons (breathing effect)  
        for i in range(8):
            brightness = int(180 + (75 * (i / 7)))  # 180-255
            self.yellow_icons.append(self.create_icon_image((brightness, brightness, 0)))
        
    def create_icon_image(self, color):
        """Create a colored circle icon"""
        image = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw circle with border
        draw.ellipse([4, 4, ICON_SIZE-4, ICON_SIZE-4], fill=color, outline=(64, 64, 64))
        draw.ellipse([8, 8, ICON_SIZE-8, ICON_SIZE-8], fill=color)
        
        # Add highlight for 3D effect
        highlight_color = tuple(min(255, c + 50) for c in color)
        draw.ellipse([12, 12, 32, 32], fill=highlight_color)
        
        return image
    
    def update_icon(self):
        """Update the tray icon with breathing animation"""
        if self.icon:
            # Calculate breathing phase (0-14, up and down)
            if self.breathing_phase < 7:
                index = self.breathing_phase
            else:
                index = 14 - self.breathing_phase
            
            if self.status == "working":
                # Yellow breathing animation when working
                self.icon.icon = self.yellow_icons[index]
                self.icon.title = "Claude is working..."
            else:
                # Green breathing animation when ready
                self.icon.icon = self.green_icons[index]
                self.icon.title = "Claude is ready"
            
            # Advance breathing phase
            self.breathing_phase = (self.breathing_phase + 1) % 15
    
    def status_listener(self):
        """Listen for status updates from the hook handler"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", LISTEN_PORT))  # Listen on all interfaces for WSL
        server_socket.listen(1)
        server_socket.settimeout(1)  # 1 second timeout for checking self.running
        
        print(f"Status listener started on port {LISTEN_PORT}")
        
        while self.running:
            try:
                client_socket, addr = server_socket.accept()
                data = client_socket.recv(1024).decode()
                if data in ["working", "standby"]:
                    self.status = data
                    print(f"Status changed to: {self.status}")
                elif data == "get_config":
                    # Send config back to hook handler
                    config = {'logging_enabled': self.logging_enabled}
                    client_socket.send(json.dumps(config).encode())
                client_socket.close()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listener error: {e}")
        
        server_socket.close()
    
    def icon_updater(self):
        """Update icon appearance in a separate thread"""
        while self.running:
            self.update_icon()
            # Smooth breathing animation
            time.sleep(0.15)  # 15 frames over ~2.25 seconds for full breath cycle
    
    def quit_app(self, icon, item):
        """Quit the application"""
        self.running = False
        icon.stop()
    
    def show_status(self, icon, item):
        """Show current status in a notification"""
        status_text = "Claude is working..." if self.status == "working" else "Claude is ready"
        icon.notify(status_text, "Claude Status")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.logging_enabled = config.get('logging_enabled', True)
        except Exception:
            pass
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {'logging_enabled': self.logging_enabled}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def toggle_logging(self, icon, item):
        """Toggle logging on/off"""
        self.logging_enabled = not self.logging_enabled
        self.save_config()
        status = "enabled" if self.logging_enabled else "disabled"
        icon.notify(f"Logging {status}", "Claude Notifier")
    
    def run(self):
        """Run the system tray application"""
        # Start listener thread
        listener_thread = threading.Thread(target=self.status_listener, daemon=True)
        listener_thread.start()
        
        # Start icon updater thread
        updater_thread = threading.Thread(target=self.icon_updater, daemon=True)
        updater_thread.start()
        
        # Create menu
        menu = Menu(
            MenuItem("Status", self.show_status),
            MenuItem("Logging", self.toggle_logging, checked=lambda item: self.logging_enabled),
            Menu.SEPARATOR,
            MenuItem("Quit", self.quit_app)
        )
        
        # Create and run tray icon
        self.icon = pystray.Icon(
            "claude_status",
            self.green_icons[0],  # Start with dimmest green
            "Claude Status - Ready",
            menu
        )
        
        self.icon.run()

def main():
    # Check if required libraries are available
    try:
        import PIL
        import pystray
    except ImportError:
        print("Required libraries not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "pystray"])
        print("Libraries installed. Please restart the application.")
        return
    
    app = ClaudeTrayApp()
    app.run()

if __name__ == "__main__":
    main()