"""
UI Application Module

Provides a graphical user interface for the AI assistant.
"""

import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from typing import Optional
import threading


class AssistantUI:
    """
    Graphical User Interface for AI Assistant
    
    Displays assistant status, command history, and provides
    visual feedback for user interactions.
    """
    
    def __init__(self, title: str = "AI Assistant"):
        self.logger = logging.getLogger(__name__)
        self.title = title
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # State variables
        self.is_listening = False
        self.is_processing = False
        
        # Setup UI components
        self._setup_ui()
        
        # Configure styles
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Status.TLabel', font=('Arial', 12))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Active.TLabel', foreground='green', font=('Arial', 12, 'bold'))
        style.configure('Inactive.TLabel', foreground='gray', font=('Arial', 12))
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🤖 AI Voice Assistant",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicators
        ttk.Label(status_frame, text="Wake Word Detection:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.wake_word_status = ttk.Label(status_frame, text="Inactive", style='Inactive.TLabel')
        self.wake_word_status.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(status_frame, text="Speech Recognition:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.stt_status = ttk.Label(status_frame, text="Inactive", style='Inactive.TLabel')
        self.stt_status.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(status_frame, text="Current State:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.state_label = ttk.Label(status_frame, text="Idle", style='Status.TLabel')
        self.state_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Activity Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Activity log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
        
        # Configure text tags for colored output
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('command', foreground='purple', font=('Consolas', 10, 'bold'))
        
        # Control Frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        control_frame.columnconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Listening",
            command=self.on_start_clicked
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.on_stop_clicked,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log
        )
        self.clear_button.grid(row=0, column=2, padx=5)
        
        # Initial log message
        self.log_message("AI Assistant initialized. Click 'Start Listening' to begin.", 'info')
    
    def set_wake_word_active(self, active: bool):
        """Update wake word detection status"""
        if active:
            self.wake_word_status.config(text="Active", style='Active.TLabel')
        else:
            self.wake_word_status.config(text="Inactive", style='Inactive.TLabel')
    
    def set_stt_active(self, active: bool):
        """Update speech recognition status"""
        if active:
            self.stt_status.config(text="Active", style='Active.TLabel')
        else:
            self.stt_status.config(text="Inactive", style='Inactive.TLabel')
    
    def set_state(self, state: str):
        """Update current state display"""
        self.state_label.config(text=state)
    
    def log_message(self, message: str, level: str = 'info'):
        """
        Add a message to the activity log
        
        Args:
            message: Message to log
            level: Log level (info, success, error, warning, command)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def log_wake_word(self, wake_word: str, confidence: float):
        """Log wake word detection"""
        self.log_message(f"🎤 Wake word detected: '{wake_word}' (confidence: {confidence:.2f})", 'success')
    
    def log_command(self, command: str):
        """Log recognized command"""
        self.log_message(f"📝 Command: '{command}'", 'command')
    
    def log_intent(self, intent: str, confidence: float):
        """Log parsed intent"""
        self.log_message(f"🎯 Intent: {intent} (confidence: {confidence:.2f})", 'info')
    
    def log_action(self, action: str, success: bool):
        """Log action execution"""
        level = 'success' if success else 'error'
        icon = '✅' if success else '❌'
        self.log_message(f"{icon} {action}", level)
    
    def log_error(self, error: str):
        """Log error message"""
        self.log_message(f"❌ Error: {error}", 'error')
    
    def clear_log(self):
        """Clear the activity log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Log cleared", 'info')
    
    def on_start_clicked(self):
        """Handle start button click"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_message("Starting assistant...", 'info')
        
        # Trigger start callback if set
        if hasattr(self, 'start_callback') and self.start_callback:
            threading.Thread(target=self.start_callback, daemon=True).start()
    
    def on_stop_clicked(self):
        """Handle stop button click"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Stopping assistant...", 'warning')
        
        # Trigger stop callback if set
        if hasattr(self, 'stop_callback') and self.stop_callback:
            self.stop_callback()
    
    def set_start_callback(self, callback):
        """Set callback for start button"""
        self.start_callback = callback
    
    def set_stop_callback(self, callback):
        """Set callback for stop button"""
        self.stop_callback = callback
    
    def run(self):
        """Start the UI main loop"""
        self.logger.info("Starting UI")
        self.root.mainloop()
    
    def close(self):
        """Close the UI"""
        self.root.quit()
        self.root.destroy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_start():
        """Example start callback"""
        import time
        ui.set_wake_word_active(True)
        ui.set_stt_active(True)
        ui.set_state("Listening")
        
        # Simulate some activity
        time.sleep(1)
        ui.log_wake_word("hey assistant", 0.95)
        
        time.sleep(0.5)
        ui.set_state("Processing")
        ui.log_command("open firefox")
        
        time.sleep(0.5)
        ui.log_intent("open_app", 0.92)
        
        time.sleep(0.5)
        ui.log_action("Opened firefox", True)
        
        ui.set_state("Listening")
    
    def on_stop():
        """Example stop callback"""
        ui.set_wake_word_active(False)
        ui.set_stt_active(False)
        ui.set_state("Idle")
        ui.log_message("Assistant stopped", 'warning')
    
    # Create UI
    ui = AssistantUI()
    ui.set_start_callback(on_start)
    ui.set_stop_callback(on_stop)
    
    # Run
    ui.run()
