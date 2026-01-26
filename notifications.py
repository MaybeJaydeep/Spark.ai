#!/usr/bin/env python3
"""
Notifications Module for AI Assistant

Provides cross-platform notification functionality.
"""

import os
import platform
import subprocess
from typing import Optional, Dict, Any
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationManager:
    """
    Cross-platform notification manager
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.enabled = True
        self.fallback_to_console = True
    
    def show_notification(self, title: str, message: str, 
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, icon: str = None) -> bool:
        """
        Show a system notification
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            duration: Duration in milliseconds
            icon: Optional icon path
            
        Returns:
            True if notification was shown successfully
        """
        if not self.enabled:
            return False
        
        try:
            if self.system == "windows":
                return self._show_windows_notification(title, message, notification_type, duration)
            elif self.system == "linux":
                return self._show_linux_notification(title, message, notification_type, duration, icon)
            elif self.system == "darwin":
                return self._show_macos_notification(title, message, notification_type)
            else:
                return self._show_console_notification(title, message, notification_type)
                
        except Exception as e:
            if self.fallback_to_console:
                return self._show_console_notification(title, message, notification_type)
            return False
    
    def _show_windows_notification(self, title: str, message: str, 
                                  notification_type: NotificationType, duration: int) -> bool:
        """Show notification on Windows using PowerShell"""
        try:
            # Map notification types to Windows toast types
            type_mapping = {
                NotificationType.INFO: "Information",
                NotificationType.SUCCESS: "Information",
                NotificationType.WARNING: "Warning",
                NotificationType.ERROR: "Error"
            }
            
            toast_type = type_mapping.get(notification_type, "Information")
            
            # PowerShell script to show toast notification
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::{toast_type}
            $notification.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::{toast_type}
            $notification.BalloonTipText = "{message}"
            $notification.BalloonTipTitle = "{title}"
            $notification.Visible = $true
            $notification.ShowBalloonTip({duration})
            Start-Sleep -Seconds 1
            $notification.Dispose()
            '''
            
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=10
            )
            return True
            
        except Exception:
            return False
    
    def _show_linux_notification(self, title: str, message: str, 
                                notification_type: NotificationType, duration: int, 
                                icon: str = None) -> bool:
        """Show notification on Linux using notify-send"""
        try:
            # Map notification types to urgency levels
            urgency_mapping = {
                NotificationType.INFO: "normal",
                NotificationType.SUCCESS: "normal",
                NotificationType.WARNING: "normal",
                NotificationType.ERROR: "critical"
            }
            
            urgency = urgency_mapping.get(notification_type, "normal")
            
            # Build notify-send command
            cmd = ["notify-send"]
            cmd.extend(["-u", urgency])
            cmd.extend(["-t", str(duration)])
            
            if icon:
                cmd.extend(["-i", icon])
            else:
                # Default icons based on type
                icon_mapping = {
                    NotificationType.INFO: "dialog-information",
                    NotificationType.SUCCESS: "dialog-information",
                    NotificationType.WARNING: "dialog-warning",
                    NotificationType.ERROR: "dialog-error"
                }
                default_icon = icon_mapping.get(notification_type, "dialog-information")
                cmd.extend(["-i", default_icon])
            
            cmd.extend([title, message])
            
            subprocess.run(cmd, capture_output=True, timeout=5)
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try alternative methods
            return self._show_linux_alternative(title, message)
    
    def _show_linux_alternative(self, title: str, message: str) -> bool:
        """Alternative Linux notification methods"""
        try:
            # Try zenity
            subprocess.run([
                "zenity", "--info", 
                f"--title={title}", 
                f"--text={message}",
                "--timeout=5"
            ], capture_output=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # Try kdialog
            subprocess.run([
                "kdialog", "--msgbox", f"{title}\n{message}"
            ], capture_output=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def _show_macos_notification(self, title: str, message: str, 
                                notification_type: NotificationType) -> bool:
        """Show notification on macOS using osascript"""
        try:
            # Map notification types to sounds
            sound_mapping = {
                NotificationType.INFO: "Glass",
                NotificationType.SUCCESS: "Glass",
                NotificationType.WARNING: "Sosumi",
                NotificationType.ERROR: "Basso"
            }
            
            sound = sound_mapping.get(notification_type, "Glass")
            
            script = f'''
            display notification "{message}" with title "{title}" sound name "{sound}"
            '''
            
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5
            )
            return True
            
        except Exception:
            return False
    
    def _show_console_notification(self, title: str, message: str, 
                                  notification_type: NotificationType) -> bool:
        """Fallback console notification"""
        # Map notification types to console symbols
        symbol_mapping = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌"
        }
        
        symbol = symbol_mapping.get(notification_type, "ℹ️")
        
        print(f"\n{symbol} {title}")
        print(f"   {message}")
        print()
        
        return True
    
    def show_command_result(self, command: str, success: bool, message: str = None):
        """
        Show notification for command execution result
        
        Args:
            command: Command that was executed
            success: Whether command succeeded
            message: Optional custom message
        """
        if success:
            title = "Command Executed"
            msg = message or f"Successfully executed: {command}"
            notification_type = NotificationType.SUCCESS
        else:
            title = "Command Failed"
            msg = message or f"Failed to execute: {command}"
            notification_type = NotificationType.ERROR
        
        self.show_notification(title, msg, notification_type)
    
    def show_timer_notification(self, timer_name: str, duration: str):
        """
        Show notification for timer completion
        
        Args:
            timer_name: Name of the timer
            duration: Timer duration
        """
        title = "Timer Finished"
        message = f"Timer '{timer_name}' ({duration}) has finished!"
        self.show_notification(title, message, NotificationType.INFO)
    
    def show_wake_word_notification(self, wake_word: str):
        """
        Show notification for wake word detection
        
        Args:
            wake_word: Detected wake word
        """
        title = "Wake Word Detected"
        message = f"Detected: '{wake_word}' - Listening for command..."
        self.show_notification(title, message, NotificationType.INFO, duration=2000)
    
    def show_error_notification(self, error_type: str, error_message: str):
        """
        Show notification for errors
        
        Args:
            error_type: Type of error
            error_message: Error message
        """
        title = f"Error: {error_type}"
        self.show_notification(title, error_message, NotificationType.ERROR)
    
    def show_system_notification(self, metric_name: str, value: str, threshold_exceeded: bool = False):
        """
        Show notification for system metrics
        
        Args:
            metric_name: Name of the metric
            value: Current value
            threshold_exceeded: Whether threshold was exceeded
        """
        if threshold_exceeded:
            title = "System Alert"
            message = f"{metric_name}: {value} (threshold exceeded)"
            notification_type = NotificationType.WARNING
        else:
            title = "System Status"
            message = f"{metric_name}: {value}"
            notification_type = NotificationType.INFO
        
        self.show_notification(title, message, notification_type)
    
    def enable_notifications(self):
        """Enable notifications"""
        self.enabled = True
    
    def disable_notifications(self):
        """Disable notifications"""
        self.enabled = False
    
    def is_supported(self) -> bool:
        """
        Check if notifications are supported on current platform
        
        Returns:
            True if notifications are supported
        """
        if self.system == "windows":
            return True  # PowerShell is available on all Windows systems
        elif self.system == "linux":
            # Check if notify-send is available
            try:
                subprocess.run(["which", "notify-send"], capture_output=True, check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        elif self.system == "darwin":
            return True  # osascript is available on all macOS systems
        else:
            return False
    
    def test_notification(self):
        """Test notification system"""
        if self.is_supported():
            self.show_notification(
                "AI Assistant",
                "Notification system is working!",
                NotificationType.SUCCESS
            )
        else:
            self._show_console_notification(
                "AI Assistant",
                "Notification system test (console fallback)",
                NotificationType.INFO
            )


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


# Convenience functions
def notify(title: str, message: str, notification_type: NotificationType = NotificationType.INFO):
    """Show a notification"""
    manager = get_notification_manager()
    manager.show_notification(title, message, notification_type)


def notify_success(title: str, message: str):
    """Show a success notification"""
    notify(title, message, NotificationType.SUCCESS)


def notify_error(title: str, message: str):
    """Show an error notification"""
    notify(title, message, NotificationType.ERROR)


def notify_warning(title: str, message: str):
    """Show a warning notification"""
    notify(title, message, NotificationType.WARNING)


if __name__ == "__main__":
    # Test notification system
    print("🔔 Testing Notification System")
    print("=" * 40)
    
    manager = NotificationManager()
    
    print(f"Platform: {platform.system()}")
    print(f"Notifications supported: {manager.is_supported()}")
    
    # Test different notification types
    print("\nTesting different notification types...")
    
    manager.show_notification("Test Info", "This is an info notification", NotificationType.INFO)
    
    import time
    time.sleep(1)
    
    manager.show_notification("Test Success", "This is a success notification", NotificationType.SUCCESS)
    
    time.sleep(1)
    
    manager.show_notification("Test Warning", "This is a warning notification", NotificationType.WARNING)
    
    time.sleep(1)
    
    manager.show_notification("Test Error", "This is an error notification", NotificationType.ERROR)
    
    # Test convenience functions
    print("\nTesting convenience functions...")
    
    time.sleep(1)
    notify_success("Command Executed", "Test command completed successfully")
    
    time.sleep(1)
    manager.show_timer_notification("Test Timer", "5 minutes")
    
    print("\n✅ Notification system test complete!")