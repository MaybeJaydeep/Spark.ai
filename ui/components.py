#!/usr/bin/env python3
"""
Professional UI Components for AI Assistant

Provides reusable, styled components:
- Professional cards and panels
- Advanced data visualization widgets
- Interactive controls with animations
- Accessibility-compliant components
- Responsive layout components
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Any, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTkinter
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from ui.themes import get_theme_manager


class ProfessionalCard(ctk.CTkFrame):
    """Professional card component with elevation and styling"""
    
    def __init__(self, parent, title: str = "", subtitle: str = "", 
                 icon: str = "", elevation: int = 2, **kwargs):
        
        theme = get_theme_manager().get_current_theme()
        
        super().__init__(
            parent,
            corner_radius=12,
            border_width=0 if elevation == 0 else 1,
            border_color=theme.colors.secondary if theme else "gray",
            **kwargs
        )
        
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.elevation = elevation
        
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup card layout"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header section
        if self.title or self.icon:
            header_frame = ctk.CTkFrame(self, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            if self.icon:
                icon_label = ctk.CTkLabel(
                    header_frame,
                    text=self.icon,
                    font=ctk.CTkFont(size=24)
                )
                icon_label.grid(row=0, column=0, padx=(0, 15), pady=0)
            
            if self.title:
                title_label = ctk.CTkLabel(
                    header_frame,
                    text=self.title,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    anchor="w"
                )
                title_label.grid(row=0, column=1, sticky="ew", pady=0)
            
            if self.subtitle:
                subtitle_label = ctk.CTkLabel(
                    header_frame,
                    text=self.subtitle,
                    font=ctk.CTkFont(size=12),
                    text_color=("gray60", "gray40"),
                    anchor="w"
                )
                subtitle_label.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        
        # Content area (to be populated by subclasses)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.grid_rowconfigure(1, weight=1)


class StatisticCard(ProfessionalCard):
    """Card for displaying statistics with trend indicators"""
    
    def __init__(self, parent, title: str, value: str, 
                 trend: Optional[float] = None, trend_label: str = "",
                 icon: str = "", color: str = "blue", **kwargs):
        
        super().__init__(parent, title=title, icon=icon, **kwargs)
        
        self.value = value
        self.trend = trend
        self.trend_label = trend_label
        self.color = color
        
        self._setup_content()
    
    def _setup_content(self):
        """Setup statistic content"""
        # Main value
        self.value_label = ctk.CTkLabel(
            self.content_frame,
            text=self.value,
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        self.value_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Trend indicator
        if self.trend is not None:
            trend_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            trend_frame.grid(row=1, column=0, sticky="w")
            
            trend_icon = "📈" if self.trend > 0 else "📉" if self.trend < 0 else "➡️"
            trend_color = "green" if self.trend > 0 else "red" if self.trend < 0 else "gray"
            
            trend_icon_label = ctk.CTkLabel(
                trend_frame,
                text=trend_icon,
                font=ctk.CTkFont(size=16)
            )
            trend_icon_label.grid(row=0, column=0, padx=(0, 5))
            
            trend_text = f"{abs(self.trend):.1f}%"
            if self.trend_label:
                trend_text += f" {self.trend_label}"
            
            trend_label = ctk.CTkLabel(
                trend_frame,
                text=trend_text,
                font=ctk.CTkFont(size=12),
                text_color=trend_color
            )
            trend_label.grid(row=0, column=1)
    
    def update_value(self, new_value: str, new_trend: Optional[float] = None):
        """Update the statistic value and trend"""
        self.value = new_value
        self.value_label.configure(text=new_value)
        
        if new_trend is not None:
            self.trend = new_trend
            # Update trend display (would need to recreate trend frame)


class ChartCard(ProfessionalCard):
    """Card containing a matplotlib chart"""
    
    def __init__(self, parent, title: str, chart_type: str = "line",
                 width: int = 400, height: int = 300, **kwargs):
        
        super().__init__(parent, title=title, **kwargs)
        
        self.chart_type = chart_type
        self.width = width
        self.height = height
        
        self._setup_chart()
    
    def _setup_chart(self):
        """Setup matplotlib chart"""
        # Create figure
        self.figure = Figure(figsize=(self.width/100, self.height/100), dpi=100)
        self.figure.patch.set_facecolor('#2b2b2b')
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        
        # Create canvas
        self.canvas = FigureCanvasTkinter(self.figure, self.content_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def update_data(self, x_data: List, y_data: List, 
                   labels: Optional[List[str]] = None, colors: Optional[List[str]] = None):
        """Update chart data"""
        self.ax.clear()
        self.ax.set_facecolor('#2b2b2b')
        
        if self.chart_type == "line":
            self.ax.plot(x_data, y_data, linewidth=2, color=colors[0] if colors else '#3b82f6')
            self.ax.fill_between(x_data, y_data, alpha=0.3, color=colors[0] if colors else '#3b82f6')
        
        elif self.chart_type == "bar":
            bars = self.ax.bar(x_data, y_data, color=colors if colors else '#3b82f6')
            if labels:
                self.ax.set_xticks(x_data)
                self.ax.set_xticklabels(labels, rotation=45)
        
        elif self.chart_type == "pie":
            self.ax.pie(y_data, labels=labels, colors=colors, autopct='%1.1f%%')
        
        # Style the chart
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        self.figure.tight_layout()
        self.canvas.draw()


class ProgressCard(ProfessionalCard):
    """Card with progress indicators"""
    
    def __init__(self, parent, title: str, progress: float = 0.0,
                 show_percentage: bool = True, color: str = "blue", **kwargs):
        
        super().__init__(parent, title=title, **kwargs)
        
        self.progress = max(0.0, min(1.0, progress))
        self.show_percentage = show_percentage
        self.color = color
        
        self._setup_progress()
    
    def _setup_progress(self):
        """Setup progress display"""
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.content_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progress_bar.set(self.progress)
        
        # Progress text
        if self.show_percentage:
            progress_text = f"{self.progress * 100:.1f}%"
            self.progress_label = ctk.CTkLabel(
                self.content_frame,
                text=progress_text,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.progress_label.grid(row=1, column=0, sticky="w")
    
    def update_progress(self, new_progress: float):
        """Update progress value"""
        self.progress = max(0.0, min(1.0, new_progress))
        self.progress_bar.set(self.progress)
        
        if self.show_percentage:
            progress_text = f"{self.progress * 100:.1f}%"
            self.progress_label.configure(text=progress_text)


class ActivityFeed(ctk.CTkScrollableFrame):
    """Activity feed component for displaying real-time updates"""
    
    def __init__(self, parent, max_items: int = 100, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.max_items = max_items
        self.items = []
        self.item_count = 0
        
        self.grid_columnconfigure(0, weight=1)
    
    def add_activity(self, title: str, description: str, 
                    timestamp: Optional[datetime] = None,
                    activity_type: str = "info", icon: str = ""):
        """Add new activity item"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Remove oldest items if at max capacity
        if len(self.items) >= self.max_items:
            oldest_item = self.items.pop(0)
            oldest_item.destroy()
        
        # Create activity item
        item_frame = self._create_activity_item(title, description, timestamp, activity_type, icon)
        item_frame.grid(row=self.item_count, column=0, sticky="ew", padx=5, pady=2)
        
        self.items.append(item_frame)
        self.item_count += 1
        
        # Auto-scroll to bottom
        self._parent_canvas.yview_moveto(1.0)
    
    def _create_activity_item(self, title: str, description: str, 
                            timestamp: datetime, activity_type: str, icon: str):
        """Create individual activity item"""
        item_frame = ctk.CTkFrame(self, height=80)
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        if not icon:
            icon_map = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌",
                "command": "🎤",
                "system": "⚙️"
            }
            icon = icon_map.get(activity_type, "📝")
        
        icon_label = ctk.CTkLabel(
            item_frame,
            text=icon,
            font=ctk.CTkFont(size=20)
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        
        # Content
        title_label = ctk.CTkLabel(
            item_frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=(15, 5))
        
        desc_label = ctk.CTkLabel(
            item_frame,
            text=description,
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        desc_label.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=(0, 15))
        
        # Timestamp
        time_str = timestamp.strftime("%H:%M:%S")
        time_label = ctk.CTkLabel(
            item_frame,
            text=time_str,
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        time_label.grid(row=0, column=2, padx=15, pady=15, sticky="ne")
        
        return item_frame
    
    def clear_activities(self):
        """Clear all activities"""
        for item in self.items:
            item.destroy()
        self.items.clear()
        self.item_count = 0


class CommandPalette(ctk.CTkToplevel):
    """Professional command palette for quick actions"""
    
    def __init__(self, parent, commands: Dict[str, Callable], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.commands = commands
        self.filtered_commands = list(commands.keys())
        
        self._setup_window()
        self._setup_layout()
        self._bind_events()
    
    def _setup_window(self):
        """Setup command palette window"""
        self.title("Command Palette")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(self.master)
        self.grab_set()
        
        # Position in center of parent
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width // 2) - 300
        y = parent_y + (parent_height // 2) - 200
        
        self.geometry(f"600x400+{x}+{y}")
    
    def _setup_layout(self):
        """Setup command palette layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Type to search commands...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.search_entry.focus()
        
        # Commands list
        self.commands_frame = ctk.CTkScrollableFrame(self)
        self.commands_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.commands_frame.grid_columnconfigure(0, weight=1)
        
        self._update_commands_list()
    
    def _bind_events(self):
        """Bind keyboard events"""
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        self.search_entry.bind("<Return>", self._execute_first_command)
        self.bind("<Escape>", lambda e: self.destroy())
    
    def _on_search_changed(self, event):
        """Handle search text changes"""
        search_text = self.search_entry.get().lower()
        
        if search_text:
            self.filtered_commands = [
                cmd for cmd in self.commands.keys()
                if search_text in cmd.lower()
            ]
        else:
            self.filtered_commands = list(self.commands.keys())
        
        self._update_commands_list()
    
    def _update_commands_list(self):
        """Update the commands list display"""
        # Clear existing commands
        for widget in self.commands_frame.winfo_children():
            widget.destroy()
        
        # Add filtered commands
        for i, command in enumerate(self.filtered_commands[:10]):  # Show max 10
            cmd_button = ctk.CTkButton(
                self.commands_frame,
                text=command,
                command=lambda c=command: self._execute_command(c),
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13)
            )
            cmd_button.grid(row=i, column=0, sticky="ew", pady=2)
    
    def _execute_command(self, command: str):
        """Execute selected command"""
        if command in self.commands:
            self.destroy()
            self.commands[command]()
    
    def _execute_first_command(self, event):
        """Execute first command in filtered list"""
        if self.filtered_commands:
            self._execute_command(self.filtered_commands[0])


class StatusIndicator(ctk.CTkFrame):
    """Professional status indicator with animations"""
    
    def __init__(self, parent, status: str = "idle", **kwargs):
        super().__init__(parent, height=30, **kwargs)
        
        self.status = status
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        
        self._setup_indicator()
    
    def _setup_indicator(self):
        """Setup status indicator"""
        # Status dot
        self.status_dot = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=16),
            width=20
        )
        self.status_dot.grid(row=0, column=0, padx=10, pady=5)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self,
            text=self.status.title(),
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        
        self._update_appearance()
    
    def set_status(self, status: str):
        """Update status"""
        self.status = status
        self.status_label.configure(text=status.title())
        self._update_appearance()
    
    def _update_appearance(self):
        """Update visual appearance based on status"""
        color_map = {
            "idle": "gray",
            "listening": "blue",
            "processing": "orange",
            "speaking": "green",
            "error": "red",
            "connected": "green",
            "disconnected": "red"
        }
        
        color = color_map.get(self.status.lower(), "gray")
        self.status_dot.configure(text_color=color)


class MetricsPanel(ctk.CTkFrame):
    """Panel for displaying multiple metrics"""
    
    def __init__(self, parent, metrics: Dict[str, Any], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.metrics = metrics
        self.metric_widgets = {}
        
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup metrics display"""
        self.grid_columnconfigure(0, weight=1)
        
        for i, (key, value) in enumerate(self.metrics.items()):
            metric_frame = ctk.CTkFrame(self)
            metric_frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            metric_frame.grid_columnconfigure(1, weight=1)
            
            # Metric name
            name_label = ctk.CTkLabel(
                metric_frame,
                text=key.replace('_', ' ').title() + ":",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            # Metric value
            value_label = ctk.CTkLabel(
                metric_frame,
                text=str(value),
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            )
            value_label.grid(row=0, column=1, padx=15, pady=10, sticky="e")
            
            self.metric_widgets[key] = value_label
    
    def update_metric(self, key: str, value: Any):
        """Update specific metric"""
        if key in self.metric_widgets:
            self.metric_widgets[key].configure(text=str(value))
            self.metrics[key] = value
    
    def update_all_metrics(self, new_metrics: Dict[str, Any]):
        """Update all metrics"""
        for key, value in new_metrics.items():
            self.update_metric(key, value)