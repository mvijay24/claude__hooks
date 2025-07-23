#!/usr/bin/env python3
"""
Claude Status Tray Icon with Volume Control
==========================================
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
import winsound

# Try to import pygame for volume control
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

ICON_SIZE = 64
CURRENT_DIR = Path(__file__).parent

class ClaudeTrayApp:
    def __init__(self):
        self.status = "standby"
        self.previous_status = "standby"
        self.icon = None
        self.running = True
        self.flash_state = False
        self.logging_enabled = True
        self.breathing_phase = 0  # For smooth breathing effect
        self.sound_file = r"C:\ChromeExtensions\Claude             hooks\claude-notifier\sounds\task_complete.wav"
        self.volume = 0.5  # 50% volume by default
        
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
        """Update icon based on current status with breathing effect"""
        if not self.icon:
            return
            
        # Breathing animation cycle (0-14)
        breathing_cycle = int(time.time() * 2) % 15
        
        if breathing_cycle < 8:
            # Inhale (getting brighter)
            frame = breathing_cycle
        else:
            # Exhale (getting dimmer)
            frame = 14 - breathing_cycle
            
        if self.status == "working":
            self.icon.icon = self.yellow_icons[frame]
        else:
            self.icon.icon = self.green_icons[frame]
            
    def load_config(self):
        """Load configuration from file"""
        config_file = CURRENT_DIR / 'config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.logging_enabled = config.get('logging', True)
                    self.volume = config.get('volume', 0.5)
            except Exception as e:
                print(f"Failed to load config: {e}")
                
    def save_config(self):
        """Save configuration to file"""
        config_file = CURRENT_DIR / 'config.json'
        config = {
            'logging': self.logging_enabled,
            'volume': self.volume
        }
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def listen_for_status(self):
        """Listen for status updates from the hook handler"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 12345))
        server_socket.listen(5)
        server_socket.settimeout(1.0)  # 1 second timeout for checking self.running
        
        print("Tray app listening on port 12345...")
        
        while self.running:
            try:
                client_socket, addr = server_socket.accept()
                data = client_socket.recv(1024).decode().strip()
                
                if data in ["working", "standby"]:
                    self.previous_status = self.status
                    self.status = data
                    print(f"Status changed to: {self.status}")
                    
                    # Play sound when transitioning from working to standby
                    if self.previous_status == "working" and self.status == "standby":
                        self.play_notification_sound()
                        
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
        
    def play_notification_sound(self):
        """Play notification sound with volume control"""
        try:
            if PYGAME_AVAILABLE:
                # Use pygame for volume control
                sound = pygame.mixer.Sound(self.sound_file)
                sound.set_volume(self.volume)
                sound.play()
                print(f"Task complete sound played at {int(self.volume * 100)}% volume")
            else:
                # Fall back to winsound (no volume control)
                winsound.PlaySound(self.sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                print("Task complete sound played (install pygame for volume control)")
        except Exception as e:
            print(f"Failed to play sound: {e}")
    
    def animation_thread(self):
        """Update the icon animation"""
        while self.running:
            self.update_icon()
            time.sleep(0.1)  # Update every 100ms for smooth animation
            
    def toggle_logging(self, icon, item):
        """Toggle logging on/off"""
        self.logging_enabled = not self.logging_enabled
        print(f"Logging {'enabled' if self.logging_enabled else 'disabled'}")
        self.save_config()
        
    def set_volume(self, level):
        """Set volume level"""
        def handler(icon, item):
            self.volume = level
            print(f"Volume set to {int(level * 100)}%")
            self.save_config()
            # Test the new volume
            self.play_notification_sound()
        return handler
        
    def exit_app(self, icon, item):
        """Exit the application"""
        self.running = False
        icon.stop()
        
    def run(self):
        """Run the tray application"""
        # Create menu
        menu = Menu(
            MenuItem('Status: ' + self.status, None, enabled=False),
            MenuItem('---', None, enabled=False),
            MenuItem('Volume', Menu(
                MenuItem('100%', self.set_volume(1.0), 
                        checked=lambda item: self.volume == 1.0, 
                        radio=True),
                MenuItem('75%', self.set_volume(0.75), 
                        checked=lambda item: self.volume == 0.75, 
                        radio=True),
                MenuItem('50%', self.set_volume(0.5), 
                        checked=lambda item: self.volume == 0.5, 
                        radio=True),
                MenuItem('25%', self.set_volume(0.25), 
                        checked=lambda item: self.volume == 0.25, 
                        radio=True),
                MenuItem('10%', self.set_volume(0.1), 
                        checked=lambda item: self.volume == 0.1, 
                        radio=True),
            )),
            MenuItem('Test Sound', lambda icon, item: self.play_notification_sound()),
            MenuItem('---', None, enabled=False),
            MenuItem('Toggle Logging', self.toggle_logging,
                    checked=lambda item: self.logging_enabled),
            MenuItem('Exit', self.exit_app)
        )
        
        # Start listener thread
        listener_thread = threading.Thread(target=self.listen_for_status, daemon=True)
        listener_thread.start()
        
        # Start animation thread
        anim_thread = threading.Thread(target=self.animation_thread, daemon=True)
        anim_thread.start()
        
        # Create and run icon
        self.icon = pystray.Icon(
            "claude_status",
            self.green_icons[0],
            "Claude Status",
            menu
        )
        
        # Update menu dynamically
        def update_menu(icon):
            icon.menu = Menu(
                MenuItem(f'Status: {self.status}', None, enabled=False),
                MenuItem('---', None, enabled=False),
                MenuItem('Volume', Menu(
                    MenuItem('100%', self.set_volume(1.0), 
                            checked=lambda item: self.volume == 1.0, 
                            radio=True),
                    MenuItem('75%', self.set_volume(0.75), 
                            checked=lambda item: self.volume == 0.75, 
                            radio=True),
                    MenuItem('50%', self.set_volume(0.5), 
                            checked=lambda item: self.volume == 0.5, 
                            radio=True),
                    MenuItem('25%', self.set_volume(0.25), 
                            checked=lambda item: self.volume == 0.25, 
                            radio=True),
                    MenuItem('10%', self.set_volume(0.1), 
                            checked=lambda item: self.volume == 0.1, 
                            radio=True),
                )),
                MenuItem('Test Sound', lambda icon, item: self.play_notification_sound()),
                MenuItem('---', None, enabled=False),
                MenuItem('Toggle Logging', self.toggle_logging,
                        checked=lambda item: self.logging_enabled),
                MenuItem('Exit', self.exit_app)
            )
            
        self.icon.update_menu = update_menu
        self.icon.run()

if __name__ == "__main__":
    app = ClaudeTrayApp()
    app.run()