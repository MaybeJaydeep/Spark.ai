"""
System Control Module

Handles system-level operations like volume control, screenshots,
power management, and other OS-level functions.
"""

import logging
import subprocess
import platform
import os
from datetime import datetime
from typing import Optional, Tuple


class SystemController:
    """
    System Controller
    
    Manages system-level operations across different platforms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
    
    # Volume Control
    
    def volume_up(self, amount: int = 10) -> bool:
        """
        Increase system volume
        
        Args:
            amount: Percentage to increase (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.system == "windows":
                return self._volume_up_windows(amount)
            elif self.system == "linux":
                return self._volume_up_linux(amount)
            elif self.system == "darwin":
                return self._volume_up_macos(amount)
            else:
                self.logger.error(f"Unsupported platform: {self.system}")
                return False
        except Exception as e:
            self.logger.error(f"Error increasing volume: {e}")
            return False
    
    def volume_down(self, amount: int = 10) -> bool:
        """
        Decrease system volume
        
        Args:
            amount: Percentage to decrease (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.system == "windows":
                return self._volume_down_windows(amount)
            elif self.system == "linux":
                return self._volume_down_linux(amount)
            elif self.system == "darwin":
                return self._volume_down_macos(amount)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error decreasing volume: {e}")
            return False
    
    def mute(self) -> bool:
        """Mute system audio"""
        try:
            if self.system == "windows":
                return self._mute_windows()
            elif self.system == "linux":
                return self._mute_linux()
            elif self.system == "darwin":
                return self._mute_macos()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error muting: {e}")
            return False
    
    def unmute(self) -> bool:
        """Unmute system audio"""
        try:
            if self.system == "windows":
                return self._unmute_windows()
            elif self.system == "linux":
                return self._unmute_linux()
            elif self.system == "darwin":
                return self._unmute_macos()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error unmuting: {e}")
            return False
    
    # Windows Volume Methods
    
    def _volume_up_windows(self, amount: int) -> bool:
        """Increase volume on Windows using nircmd or PowerShell"""
        try:
            # Try using PowerShell
            script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]175)"
            for _ in range(amount // 2):  # Each press increases by ~2%
                subprocess.run(["powershell", "-Command", script], 
                             capture_output=True)
            self.logger.info(f"Increased volume on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows volume up failed: {e}")
            return False
    
    def _volume_down_windows(self, amount: int) -> bool:
        """Decrease volume on Windows"""
        try:
            script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
            for _ in range(amount // 2):
                subprocess.run(["powershell", "-Command", script],
                             capture_output=True)
            self.logger.info(f"Decreased volume on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows volume down failed: {e}")
            return False
    
    def _mute_windows(self) -> bool:
        """Mute on Windows"""
        try:
            script = "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
            subprocess.run(["powershell", "-Command", script],
                         capture_output=True)
            self.logger.info("Muted on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows mute failed: {e}")
            return False
    
    def _unmute_windows(self) -> bool:
        """Unmute on Windows (same as mute - toggle)"""
        return self._mute_windows()
    
    # Linux Volume Methods
    
    def _volume_up_linux(self, amount: int) -> bool:
        """Increase volume on Linux using amixer"""
        try:
            subprocess.run(["amixer", "set", "Master", f"{amount}%+"],
                         capture_output=True)
            self.logger.info(f"Increased volume on Linux")
            return True
        except FileNotFoundError:
            # Try pactl as fallback
            try:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{amount}%"],
                             capture_output=True)
                return True
            except Exception as e:
                self.logger.error(f"Linux volume up failed: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Linux volume up failed: {e}")
            return False
    
    def _volume_down_linux(self, amount: int) -> bool:
        """Decrease volume on Linux"""
        try:
            subprocess.run(["amixer", "set", "Master", f"{amount}%-"],
                         capture_output=True)
            self.logger.info(f"Decreased volume on Linux")
            return True
        except FileNotFoundError:
            try:
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{amount}%"],
                             capture_output=True)
                return True
            except Exception as e:
                self.logger.error(f"Linux volume down failed: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Linux volume down failed: {e}")
            return False
    
    def _mute_linux(self) -> bool:
        """Mute on Linux"""
        try:
            subprocess.run(["amixer", "set", "Master", "mute"],
                         capture_output=True)
            self.logger.info("Muted on Linux")
            return True
        except FileNotFoundError:
            try:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"],
                             capture_output=True)
                return True
            except Exception as e:
                self.logger.error(f"Linux mute failed: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Linux mute failed: {e}")
            return False
    
    def _unmute_linux(self) -> bool:
        """Unmute on Linux"""
        try:
            subprocess.run(["amixer", "set", "Master", "unmute"],
                         capture_output=True)
            self.logger.info("Unmuted on Linux")
            return True
        except FileNotFoundError:
            try:
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"],
                             capture_output=True)
                return True
            except Exception as e:
                self.logger.error(f"Linux unmute failed: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Linux unmute failed: {e}")
            return False
    
    # macOS Volume Methods
    
    def _volume_up_macos(self, amount: int) -> bool:
        """Increase volume on macOS"""
        try:
            # Get current volume
            result = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"],
                                  capture_output=True, text=True)
            current = int(result.stdout.strip())
            new_volume = min(100, current + amount)
            
            subprocess.run(["osascript", "-e", f"set volume output volume {new_volume}"],
                         capture_output=True)
            self.logger.info(f"Increased volume on macOS to {new_volume}")
            return True
        except Exception as e:
            self.logger.error(f"macOS volume up failed: {e}")
            return False
    
    def _volume_down_macos(self, amount: int) -> bool:
        """Decrease volume on macOS"""
        try:
            result = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"],
                                  capture_output=True, text=True)
            current = int(result.stdout.strip())
            new_volume = max(0, current - amount)
            
            subprocess.run(["osascript", "-e", f"set volume output volume {new_volume}"],
                         capture_output=True)
            self.logger.info(f"Decreased volume on macOS to {new_volume}")
            return True
        except Exception as e:
            self.logger.error(f"macOS volume down failed: {e}")
            return False
    
    def _mute_macos(self) -> bool:
        """Mute on macOS"""
        try:
            subprocess.run(["osascript", "-e", "set volume output muted true"],
                         capture_output=True)
            self.logger.info("Muted on macOS")
            return True
        except Exception as e:
            self.logger.error(f"macOS mute failed: {e}")
            return False
    
    def _unmute_macos(self) -> bool:
        """Unmute on macOS"""
        try:
            subprocess.run(["osascript", "-e", "set volume output muted false"],
                         capture_output=True)
            self.logger.info("Unmuted on macOS")
            return True
        except Exception as e:
            self.logger.error(f"macOS unmute failed: {e}")
            return False
    
    # Screenshot
    
    def take_screenshot(self, filename: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Take a screenshot
        
        Args:
            filename: Optional filename for the screenshot
            
        Returns:
            Tuple of (success, filepath)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Ensure screenshots directory exists
        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, filename)
        
        try:
            if self.system == "windows":
                success = self._screenshot_windows(filepath)
            elif self.system == "linux":
                success = self._screenshot_linux(filepath)
            elif self.system == "darwin":
                success = self._screenshot_macos(filepath)
            else:
                return False, None
            
            if success:
                self.logger.info(f"Screenshot saved to: {filepath}")
                return True, filepath
            else:
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False, None
    
    def _screenshot_windows(self, filepath: str) -> bool:
        """Take screenshot on Windows"""
        try:
            # Use PowerShell with .NET
            script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
            $bitmap.Save('{filepath}')
            $graphics.Dispose()
            $bitmap.Dispose()
            """
            subprocess.run(["powershell", "-Command", script], capture_output=True)
            return os.path.exists(filepath)
        except Exception as e:
            self.logger.error(f"Windows screenshot failed: {e}")
            return False
    
    def _screenshot_linux(self, filepath: str) -> bool:
        """Take screenshot on Linux"""
        try:
            # Try gnome-screenshot first
            subprocess.run(["gnome-screenshot", "-f", filepath], capture_output=True)
            if os.path.exists(filepath):
                return True
            
            # Try scrot as fallback
            subprocess.run(["scrot", filepath], capture_output=True)
            return os.path.exists(filepath)
        except Exception as e:
            self.logger.error(f"Linux screenshot failed: {e}")
            return False
    
    def _screenshot_macos(self, filepath: str) -> bool:
        """Take screenshot on macOS"""
        try:
            subprocess.run(["screencapture", filepath], capture_output=True)
            return os.path.exists(filepath)
        except Exception as e:
            self.logger.error(f"macOS screenshot failed: {e}")
            return False
    
    # Power Management
    
    def shutdown(self, confirm: bool = True) -> bool:
        """
        Shutdown the system
        
        Args:
            confirm: Require confirmation before shutdown
            
        Returns:
            True if command executed, False otherwise
        """
        if confirm:
            self.logger.warning("Shutdown requested but confirmation required")
            return False
        
        try:
            if self.system == "windows":
                subprocess.run(["shutdown", "/s", "/t", "0"], capture_output=True)
            elif self.system in ["linux", "darwin"]:
                subprocess.run(["sudo", "shutdown", "-h", "now"], capture_output=True)
            
            self.logger.info("Shutdown command executed")
            return True
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            return False
    
    def restart(self, confirm: bool = True) -> bool:
        """
        Restart the system
        
        Args:
            confirm: Require confirmation before restart
            
        Returns:
            True if command executed, False otherwise
        """
        if confirm:
            self.logger.warning("Restart requested but confirmation required")
            return False
        
        try:
            if self.system == "windows":
                subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True)
            elif self.system in ["linux", "darwin"]:
                subprocess.run(["sudo", "shutdown", "-r", "now"], capture_output=True)
            
            self.logger.info("Restart command executed")
            return True
        except Exception as e:
            self.logger.error(f"Restart failed: {e}")
            return False
    
    def lock_screen(self) -> bool:
        """Lock the screen"""
        try:
            if self.system == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"],
                             capture_output=True)
            elif self.system == "linux":
                # Try multiple lock commands
                for cmd in [["gnome-screensaver-command", "-l"],
                           ["xdg-screensaver", "lock"],
                           ["loginctl", "lock-session"]]:
                    try:
                        subprocess.run(cmd, capture_output=True)
                        break
                    except FileNotFoundError:
                        continue
            elif self.system == "darwin":
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
                             capture_output=True)
            
            self.logger.info("Screen locked")
            return True
        except Exception as e:
            self.logger.error(f"Lock screen failed: {e}")
            return False
    
    # System Information
    
    # Media Control
    
    def play_media(self) -> bool:
        """Play/resume media (sends Play/Pause key)"""
        try:
            if self.system == "windows":
                return self._play_media_windows()
            elif self.system == "linux":
                return self._play_media_linux()
            elif self.system == "darwin":
                return self._play_media_macos()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error playing media: {e}")
            return False
    
    def pause_media(self) -> bool:
        """Pause media (sends Play/Pause key - same as play, toggles)"""
        return self.play_media()  # Play/Pause is a toggle
    
    def next_track(self) -> bool:
        """Skip to next track"""
        try:
            if self.system == "windows":
                return self._next_track_windows()
            elif self.system == "linux":
                return self._next_track_linux()
            elif self.system == "darwin":
                return self._next_track_macos()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error skipping to next track: {e}")
            return False
    
    def previous_track(self) -> bool:
        """Go to previous track"""
        try:
            if self.system == "windows":
                return self._previous_track_windows()
            elif self.system == "linux":
                return self._previous_track_linux()
            elif self.system == "darwin":
                return self._previous_track_macos()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error going to previous track: {e}")
            return False
    
    # Windows Media Control Methods
    
    def _play_media_windows(self) -> bool:
        """Send Play/Pause media key on Windows"""
        try:
            # VK_MEDIA_PLAY_PAUSE = 0xB3
            script = """
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class MediaKeys {
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                public static void PlayPause() {
                    keybd_event(0xB3, 0, 0, 0);
                    keybd_event(0xB3, 0, 2, 0);
                }
            }
"@
            [MediaKeys]::PlayPause()
            """
            subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=2)
            self.logger.info("Sent Play/Pause media key on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows play/pause failed: {e}")
            # Fallback: try sending spacebar (works in many players)
            try:
                script = "(New-Object -ComObject WScript.Shell).SendKeys(' ')"
                subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=1)
                return True
            except:
                return False
    
    def _next_track_windows(self) -> bool:
        """Send Next Track media key on Windows"""
        try:
            # VK_MEDIA_NEXT_TRACK = 0xB0
            script = """
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class MediaKeys {
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                public static void NextTrack() {
                    keybd_event(0xB0, 0, 0, 0);
                    keybd_event(0xB0, 0, 2, 0);
                }
            }
"@
            [MediaKeys]::NextTrack()
            """
            subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=2)
            self.logger.info("Sent Next Track media key on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows next track failed: {e}")
            return False
    
    def _previous_track_windows(self) -> bool:
        """Send Previous Track media key on Windows"""
        try:
            # VK_MEDIA_PREV_TRACK = 0xB1
            script = """
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class MediaKeys {
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                public static void PrevTrack() {
                    keybd_event(0xB1, 0, 0, 0);
                    keybd_event(0xB1, 0, 2, 0);
                }
            }
"@
            [MediaKeys]::PrevTrack()
            """
            subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=2)
            self.logger.info("Sent Previous Track media key on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Windows previous track failed: {e}")
            return False
    
    # Linux Media Control Methods
    
    def _play_media_linux(self) -> bool:
        """Send Play/Pause on Linux using playerctl"""
        try:
            subprocess.run(["playerctl", "play-pause"], capture_output=True, timeout=2)
            return True
        except FileNotFoundError:
            self.logger.warning("playerctl not found, media control unavailable")
            return False
        except Exception as e:
            self.logger.error(f"Linux play/pause failed: {e}")
            return False
    
    def _next_track_linux(self) -> bool:
        """Send Next Track on Linux"""
        try:
            subprocess.run(["playerctl", "next"], capture_output=True, timeout=2)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            self.logger.error(f"Linux next track failed: {e}")
            return False
    
    def _previous_track_linux(self) -> bool:
        """Send Previous Track on Linux"""
        try:
            subprocess.run(["playerctl", "previous"], capture_output=True, timeout=2)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            self.logger.error(f"Linux previous track failed: {e}")
            return False
    
    # macOS Media Control Methods
    
    def _play_media_macos(self) -> bool:
        """Send Play/Pause on macOS"""
        try:
            subprocess.run(["osascript", "-e", "tell application \"System Events\" to key code 49"], 
                         capture_output=True, timeout=2)
            return True
        except Exception as e:
            self.logger.error(f"macOS play/pause failed: {e}")
            return False
    
    def _next_track_macos(self) -> bool:
        """Send Next Track on macOS"""
        try:
            subprocess.run(["osascript", "-e", "tell application \"System Events\" to key code 144"], 
                         capture_output=True, timeout=2)
            return True
        except Exception as e:
            self.logger.error(f"macOS next track failed: {e}")
            return False
    
    def _previous_track_macos(self) -> bool:
        """Send Previous Track on macOS"""
        try:
            subprocess.run(["osascript", "-e", "tell application \"System Events\" to key code 145"], 
                         capture_output=True, timeout=2)
            return True
        except Exception as e:
            self.logger.error(f"macOS previous track failed: {e}")
            return False
    
    # System Information
    
    def get_system_info(self) -> dict:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node()
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    controller = SystemController()
    
    print("Testing SystemController:\n")
    
    # Test volume control
    print("Testing volume up...")
    controller.volume_up(5)
    
    print("\nTesting volume down...")
    controller.volume_down(5)
    
    # Test screenshot
    print("\nTaking screenshot...")
    success, filepath = controller.take_screenshot()
    if success:
        print(f"✅ Screenshot saved to: {filepath}")
    else:
        print("❌ Screenshot failed")
    
    # Get system info
    print("\nSystem Information:")
    info = controller.get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
