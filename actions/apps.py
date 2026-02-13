"""
Application Control Module

Handles opening, closing, and managing applications.
"""

import logging
import subprocess
import platform
import os
from typing import Optional, List


class AppController:
    """
    Application Controller
    
    Manages application launching and control across different platforms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.app_launch_count = 0  # Track app launches for analytics
        
        # Common application mappings (case-insensitive)
        self.app_mappings = {
            "chrome": {
                "windows": "chrome",
                "linux": "google-chrome",
                "darwin": "Google Chrome"
            },
            "google chrome": {
                "windows": "chrome",
                "linux": "google-chrome",
                "darwin": "Google Chrome"
            },
            "firefox": {
                "windows": "firefox",
                "linux": "firefox",
                "darwin": "Firefox"
            },
            "edge": {
                "windows": "msedge",
                "linux": "microsoft-edge",
                "darwin": "Microsoft Edge"
            },
            "microsoft edge": {
                "windows": "msedge",
                "linux": "microsoft-edge",
                "darwin": "Microsoft Edge"
            },
            "notepad": {
                "windows": "notepad",
                "linux": "gedit",
                "darwin": "TextEdit"
            },
            "calculator": {
                "windows": "calc",
                "linux": "gnome-calculator",
                "darwin": "Calculator"
            },
            "calc": {
                "windows": "calc",
                "linux": "gnome-calculator",
                "darwin": "Calculator"
            },
            "terminal": {
                "windows": "cmd",
                "linux": "gnome-terminal",
                "darwin": "Terminal"
            },
            "cmd": {
                "windows": "cmd",
                "linux": "gnome-terminal",
                "darwin": "Terminal"
            },
            "command prompt": {
                "windows": "cmd",
                "linux": "gnome-terminal",
                "darwin": "Terminal"
            },
            "vscode": {
                "windows": "code",
                "linux": "code",
                "darwin": "Visual Studio Code"
            },
            "visual studio code": {
                "windows": "code",
                "linux": "code",
                "darwin": "Visual Studio Code"
            },
            "spotify": {
                "windows": "spotify",
                "linux": "spotify",
                "darwin": "Spotify"
            },
            "vlc": {
                "windows": "vlc",
                "linux": "vlc",
                "darwin": "VLC"
            },
            "youtube": {
                "windows": "chrome",
                "linux": "google-chrome",
                "darwin": "Google Chrome"
            },
            "word": {
                "windows": "winword",
                "linux": "libreoffice",
                "darwin": "Microsoft Word"
            },
            "excel": {
                "windows": "excel",
                "linux": "libreoffice",
                "darwin": "Microsoft Excel"
            },
            "powerpoint": {
                "windows": "powerpnt",
                "linux": "libreoffice",
                "darwin": "Microsoft PowerPoint"
            },
            "outlook": {
                "windows": "outlook",
                "linux": "thunderbird",
                "darwin": "Microsoft Outlook"
            },
            "paint": {
                "windows": "mspaint",
                "linux": "gimp",
                "darwin": "Preview"
            },
            "file explorer": {
                "windows": "explorer",
                "linux": "nautilus",
                "darwin": "Finder"
            },
            "explorer": {
                "windows": "explorer",
                "linux": "nautilus",
                "darwin": "Finder"
            }
        }
    
    def open_app(self, app_name: str) -> bool:
        """
        Open an application
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            True if successful, False otherwise
        """
        self.app_launch_count += 1
        app_name_lower = app_name.lower().strip()
        
        # Get the executable name for this platform
        executable = self._get_executable(app_name_lower)
        
        if not executable:
            self.logger.warning(f"Unknown application: {app_name}")
            # Try to open it directly anyway
            executable = app_name
        
        try:
            if self.system == "windows":
                return self._open_windows(executable)
            elif self.system == "linux":
                return self._open_linux(executable)
            elif self.system == "darwin":
                return self._open_macos(executable)
            else:
                self.logger.error(f"Unsupported platform: {self.system}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error opening {app_name}: {e}")
            return False
    
    def _get_executable(self, app_name: str) -> Optional[str]:
        """Get the executable name for the current platform"""
        if app_name in self.app_mappings:
            return self.app_mappings[app_name].get(self.system)
        return None
    
    def _open_windows(self, executable: str) -> bool:
        """Open application on Windows"""
        try:
            # Remove .exe if present to avoid duplication
            exe_name = executable.lower()
            if not exe_name.endswith('.exe'):
                exe_name = exe_name + '.exe'
            
            # Try using start command (works for most apps)
            # Use shell=True to allow Windows to find the app in PATH
            subprocess.Popen(f'start "" "{exe_name}"', shell=True)
            self.logger.info(f"Opened {exe_name} on Windows")
            return True
        except Exception as e:
            # Try without .exe extension
            try:
                subprocess.Popen(f'start "" "{executable}"', shell=True)
                self.logger.info(f"Opened {executable} on Windows")
                return True
            except Exception as e2:
                self.logger.error(f"Failed to open on Windows: {e}, {e2}")
                return False
    
    def _open_linux(self, executable: str) -> bool:
        """Open application on Linux"""
        try:
            # Try direct execution
            subprocess.Popen([executable], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.logger.info(f"Opened {executable} on Linux")
            return True
        except FileNotFoundError:
            # Try with xdg-open as fallback
            try:
                subprocess.Popen(["xdg-open", executable],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True
            except Exception as e:
                self.logger.error(f"Failed to open on Linux: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to open on Linux: {e}")
            return False
    
    def _open_macos(self, executable: str) -> bool:
        """Open application on macOS"""
        try:
            # Use 'open' command on macOS
            subprocess.Popen(["open", "-a", executable],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            self.logger.info(f"Opened {executable} on macOS")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open on macOS: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """
        Close an application
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            True if successful, False otherwise
        """
        app_name_lower = app_name.lower().strip()
        executable = self._get_executable(app_name_lower)
        
        if not executable:
            executable = app_name
        
        try:
            if self.system == "windows":
                return self._close_windows(executable)
            elif self.system == "linux":
                return self._close_linux(executable)
            elif self.system == "darwin":
                return self._close_macos(executable)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing {app_name}: {e}")
            return False
    
    def _close_windows(self, executable: str) -> bool:
        """Close application on Windows"""
        try:
            # Use taskkill command
            subprocess.run(["taskkill", "/F", "/IM", executable],
                         capture_output=True)
            self.logger.info(f"Closed {executable} on Windows")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close on Windows: {e}")
            return False
    
    def _close_linux(self, executable: str) -> bool:
        """Close application on Linux"""
        try:
            # Use pkill command
            subprocess.run(["pkill", "-f", executable],
                         capture_output=True)
            self.logger.info(f"Closed {executable} on Linux")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close on Linux: {e}")
            return False
    
    def _close_macos(self, executable: str) -> bool:
        """Close application on macOS"""
        try:
            # Use pkill command
            subprocess.run(["pkill", "-f", executable],
                         capture_output=True)
            self.logger.info(f"Closed {executable} on macOS")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close on macOS: {e}")
            return False
    
    def search_web(self, query: str) -> bool:
        """
        Open a web search in the default browser
        
        Args:
            query: Search query
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import webbrowser
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            self.logger.info(f"Opened web search for: {query}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open web search: {e}")
            return False
    
    def search_youtube(self, query: str) -> bool:
        """
        Open a YouTube search in the default browser
        
        Args:
            query: Search query
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import webbrowser
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            self.logger.info(f"Opened YouTube search for: {query}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open YouTube search: {e}")
            return False
    
    def list_running_apps(self) -> List[str]:
        """
        List currently running applications
        
        Returns:
            List of running application names
        """
        try:
            if self.system == "windows":
                result = subprocess.run(["tasklist"], 
                                      capture_output=True, 
                                      text=True)
                # Parse tasklist output
                lines = result.stdout.split('\n')[3:]  # Skip header
                apps = [line.split()[0] for line in lines if line.strip()]
                return apps
            elif self.system in ["linux", "darwin"]:
                result = subprocess.run(["ps", "aux"], 
                                      capture_output=True, 
                                      text=True)
                lines = result.stdout.split('\n')[1:]  # Skip header
                apps = [line.split()[-1] for line in lines if line.strip()]
                return apps
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to list running apps: {e}")
            return []


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    controller = AppController()
    
    print("Testing AppController:\n")
    
    # Test opening Firefox
    print("Opening Firefox...")
    success = controller.open_app("firefox")
    print(f"Result: {'✅ Success' if success else '❌ Failed'}\n")
    
    # Test web search
    print("Opening web search...")
    success = controller.search_web("python tutorials")
    print(f"Result: {'✅ Success' if success else '❌ Failed'}\n")
