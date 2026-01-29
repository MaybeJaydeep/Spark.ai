#!/usr/bin/env python3
"""
Professional Industry-Level UI for AI Voice Assistant

Features:
- Modern Material Design 3 inspired interface
- Multi-panel dashboard layout
- Real-time analytics and visualizations
- Advanced settings and configuration
- Professional command palette
- Responsive design with themes
- Accessibility features
- Performance monitoring
- Plugin system integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Any
import threading
import queue
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTkinter
from matplotlib.figure import Figure
import numpy as np
from pathlib import Path

# Import our existing components
from ui.controller import AssistantController, AssistantSettings
from nlp.intent_parser import Intent, IntentType
from analytics import AnalyticsTracker
from performance import PerformanceMonitor
from database import AssistantDatabase


@dataclass
class UITheme:
    """Professional UI theme configuration"""
    name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    surface_color: str
    text_primary: str
    text_secondary: str
    success_color: str
    warning_color: str
    error_color: str
    info_color: str


class ThemeManager:
    """Manages UI themes and appearance"""
    
    THEMES = {
        "dark_professional": UITheme(
            name="Dark Professional",
            primary_color="#1e293b",
            secondary_color="#334155",
            accent_color="#3b82f6",
            background_color="#0f172a",
            surface_color="#1e293b",
            text_primary="#f8fafc",
            text_secondary="#cbd5e1",
            success_color="#10b981",
            warning_color="#f59e0b",
            error_color="#ef4444",
            info_color="#06b6d4"
        ),
        "light_professional": UITheme(
            name="Light Professional",
            primary_color="#ffffff",
            secondary_color="#f8fafc",
            accent_color="#3b82f6",
            background_color="#f1f5f9",
            surface_color="#ffffff",
            text_primary="#1e293b",
            text_secondary="#64748b",
            success_color="#059669",
            warning_color="#d97706",
            error_color="#dc2626",
            info_color="#0891b2"
        ),
        "blue_corporate": UITheme(
            name="Blue Corporate",
            primary_color="#1e40af",
            secondary_color="#3b82f6",
            accent_color="#60a5fa",
            background_color="#eff6ff",
            surface_color="#dbeafe",
            text_primary="#1e3a8a",
            text_secondary="#3730a3",
            success_color="#059669",
            warning_color="#d97706",
            error_color="#dc2626",
            info_color="#0891b2"
        )
    }
    
    def __init__(self):
        self.current_theme = self.THEMES["dark_professional"]
    
    def set_theme(self, theme_name: str):
        if theme_name in self.THEMES:
            self.current_theme = self.THEMES[theme_name]
            ctk.set_appearance_mode("dark" if "dark" in theme_name else "light")


class ProfessionalAssistantUI(ctk.CTk):
    """
    Industry-level professional UI for AI Voice Assistant
    
    Features:
    - Multi-panel dashboard
    - Real-time analytics
    - Advanced configuration
    - Professional command interface
    - Performance monitoring
    - Accessibility support
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.theme_manager = ThemeManager()
        self.analytics = AnalyticsTracker()
        self.performance_monitor = PerformanceMonitor()
        self.database = AssistantDatabase()
        
        # UI state
        self._ui_queue = queue.Queue()
        self._settings = AssistantSettings()
        self._current_view = "dashboard"
        self._command_history = []
        self._performance_data = {"cpu": [], "memory": [], "response_times": []}
        
        # Initialize controller
        self._controller = AssistantController(
            settings=self._settings,
            on_log=lambda msg: self._ui_queue.put(("log", msg)),
            on_status=lambda msg: self._ui_queue.put(("status", msg)),
            on_intent=lambda intent: self._ui_queue.put(("intent", intent)),
            on_result=lambda res: self._ui_queue.put(("result", res)),
        )
        
        # Setup UI
        self._setup_window()
        self._create_layout()
        self._setup_themes()
        self._start_monitoring()
        
        # Start UI update loop
        self.after(100, self._update_ui)
    
    def _setup_window(self):
        """Configure main window"""
        self.title("Spark AI Assistant - Professional Dashboard")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set icon (if available)
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _create_layout(self):
        """Create the main layout structure"""
        # Sidebar navigation
        self._create_sidebar()
        
        # Main content area
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
    
    def _create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(self.sidebar, height=80, corner_radius=0)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        logo_frame.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="🤖 Spark AI",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)
        
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Professional Assistant",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, corner_radius=0)
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard", self._show_dashboard),
            ("chat", "💬 Chat Interface", self._show_chat),
            ("analytics", "📈 Analytics", self._show_analytics),
            ("settings", "⚙️ Settings", self._show_settings),
            ("performance", "🔧 Performance", self._show_performance),
            ("help", "❓ Help & Support", self._show_help)
        ]
        
        for i, (key, text, command) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                height=50,
                corner_radius=0,
                anchor="w",
                font=ctk.CTkFont(size=14)
            )
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=2)
            self.nav_buttons[key] = btn
        
        # System status
        status_frame = ctk.CTkFrame(self.sidebar, height=120, corner_radius=0)
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(20, 0))
        status_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            status_frame,
            text="System Status",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5))
        
        self.status_labels = {}
        status_items = [
            ("assistant", "Assistant: Stopped"),
            ("wake_word", "Wake Word: OFF"),
            ("voice", "Voice: Ready")
        ]
        
        for i, (key, text) in enumerate(status_items):
            label = ctk.CTkLabel(
                status_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray40")
            )
            label.grid(row=i+1, column=0, padx=20, pady=2, sticky="w")
            self.status_labels[key] = label
    
    def _create_main_content(self):
        """Create main content area"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create different views
        self._create_dashboard_view()
        self._create_chat_view()
        self._create_analytics_view()
        self._create_settings_view()
        self._create_performance_view()
        self._create_help_view()
        
        # Show dashboard by default
        self._show_dashboard()
    
    def _create_dashboard_view(self):
        """Create dashboard view"""
        self.dashboard_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.dashboard_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Control buttons
        control_frame = ctk.CTkFrame(header_frame)
        control_frame.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Start Assistant",
            command=self._start_assistant,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Stop",
            command=self._stop_assistant,
            height=40,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(self.dashboard_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.stats_cards = {}
        stats_data = [
            ("commands", "Commands Today", "0", "📝"),
            ("uptime", "Uptime", "00:00:00", "⏱️"),
            ("accuracy", "Accuracy", "0%", "🎯"),
            ("response", "Avg Response", "0ms", "⚡")
        ]
        
        for i, (key, title, value, icon) in enumerate(stats_data):
            card = self._create_stat_card(stats_frame, title, value, icon)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.stats_cards[key] = card
        
        # Recent activity
        activity_frame = ctk.CTkFrame(self.dashboard_frame)
        activity_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.activity_text = ctk.CTkTextbox(
            activity_frame,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.activity_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(2, weight=1)
    
    def _create_chat_view(self):
        """Create chat interface view"""
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.chat_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Chat Interface",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Chat area
        chat_container = ctk.CTkFrame(self.chat_frame)
        chat_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkScrollableFrame(chat_container)
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_display.grid_columnconfigure(0, weight=1)
        
        # Input area
        input_frame = ctk.CTkFrame(self.chat_frame, height=100)
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_propagate(False)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your command or question...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.chat_entry.bind("<Return>", self._send_chat_message)
        
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.grid(row=0, column=1, padx=(10, 20), pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Send",
            command=self._send_chat_message,
            width=80,
            height=40
        ).grid(row=0, column=0, padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🎤 Voice",
            command=self._voice_input,
            width=80,
            height=40
        ).grid(row=0, column=1, padx=5)
        
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(1, weight=1)
        
        self._chat_message_count = 0
    
    def _create_analytics_view(self):
        """Create analytics view with charts"""
        self.analytics_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.analytics_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Analytics & Insights",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Charts container
        charts_frame = ctk.CTkFrame(self.analytics_frame)
        charts_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Create matplotlib figures
        self._create_analytics_charts(charts_frame)
        
        self.analytics_frame.grid_columnconfigure(0, weight=1)
        self.analytics_frame.grid_rowconfigure(1, weight=1)
    
    def _create_settings_view(self):
        """Create settings view"""
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.settings_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Settings & Configuration",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Settings container
        settings_container = ctk.CTkScrollableFrame(self.settings_frame)
        settings_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        settings_container.grid_columnconfigure(0, weight=1)
        
        self._create_settings_sections(settings_container)
        
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(1, weight=1)
    
    def _create_performance_view(self):
        """Create performance monitoring view"""
        self.performance_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.performance_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Performance Monitor",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Performance metrics
        metrics_frame = ctk.CTkFrame(self.performance_frame)
        metrics_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        metrics_frame.grid_columnconfigure((0, 1), weight=1)
        metrics_frame.grid_rowconfigure((0, 1), weight=1)
        
        self._create_performance_charts(metrics_frame)
        
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid_rowconfigure(1, weight=1)
    
    def _create_help_view(self):
        """Create help and support view"""
        self.help_frame = ctk.CTkFrame(self.main_frame)
        
        # Header
        header_frame = ctk.CTkFrame(self.help_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Help & Support",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Help content
        help_container = ctk.CTkScrollableFrame(self.help_frame)
        help_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        help_container.grid_columnconfigure(0, weight=1)
        
        self._create_help_content(help_container)
        
        self.help_frame.grid_columnconfigure(0, weight=1)
        self.help_frame.grid_rowconfigure(1, weight=1)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.status_bar.grid_propagate(False)
        self.status_bar.grid_columnconfigure(1, weight=1)
        
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.connection_status = ctk.CTkLabel(
            self.status_bar,
            text="🔴 Disconnected",
            font=ctk.CTkFont(size=12)
        )
        self.connection_status.grid(row=0, column=2, padx=10, pady=5, sticky="e")
    
    def _create_stat_card(self, parent, title, value, icon):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, height=120)
        card.grid_propagate(False)
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, padx=20, pady=(20, 5))
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        ).grid(row=1, column=0, padx=20, pady=0)
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        value_label.grid(row=2, column=0, padx=20, pady=(5, 20))
        
        # Store reference to value label for updates
        card.value_label = value_label
        return card
    
    def _create_analytics_charts(self, parent):
        """Create analytics charts"""
        # Command frequency chart
        fig1 = Figure(figsize=(6, 4), dpi=100)
        fig1.patch.set_facecolor('#2b2b2b')
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('#2b2b2b')
        ax1.set_title("Command Frequency", color='white')
        
        canvas1 = FigureCanvasTkinter(fig1, parent)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Response time chart
        fig2 = Figure(figsize=(6, 4), dpi=100)
        fig2.patch.set_facecolor('#2b2b2b')
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor('#2b2b2b')
        ax2.set_title("Response Times", color='white')
        
        canvas2 = FigureCanvasTkinter(fig2, parent)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Usage over time
        fig3 = Figure(figsize=(12, 4), dpi=100)
        fig3.patch.set_facecolor('#2b2b2b')
        ax3 = fig3.add_subplot(111)
        ax3.set_facecolor('#2b2b2b')
        ax3.set_title("Usage Over Time", color='white')
        
        canvas3 = FigureCanvasTkinter(fig3, parent)
        canvas3.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.analytics_charts = {
            'frequency': (fig1, ax1, canvas1),
            'response_time': (fig2, ax2, canvas2),
            'usage': (fig3, ax3, canvas3)
        }
    
    def _create_performance_charts(self, parent):
        """Create performance monitoring charts"""
        # CPU usage
        fig1 = Figure(figsize=(6, 4), dpi=100)
        fig1.patch.set_facecolor('#2b2b2b')
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('#2b2b2b')
        ax1.set_title("CPU Usage", color='white')
        ax1.set_ylim(0, 100)
        
        canvas1 = FigureCanvasTkinter(fig1, parent)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Memory usage
        fig2 = Figure(figsize=(6, 4), dpi=100)
        fig2.patch.set_facecolor('#2b2b2b')
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor('#2b2b2b')
        ax2.set_title("Memory Usage", color='white')
        
        canvas2 = FigureCanvasTkinter(fig2, parent)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # System metrics
        fig3 = Figure(figsize=(12, 4), dpi=100)
        fig3.patch.set_facecolor('#2b2b2b')
        ax3 = fig3.add_subplot(111)
        ax3.set_facecolor('#2b2b2b')
        ax3.set_title("System Performance", color='white')
        
        canvas3 = FigureCanvasTkinter(fig3, parent)
        canvas3.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.performance_charts = {
            'cpu': (fig1, ax1, canvas1),
            'memory': (fig2, ax2, canvas2),
            'system': (fig3, ax3, canvas3)
        }
    
    def _create_settings_sections(self, parent):
        """Create settings sections"""
        # Voice Settings
        voice_section = ctk.CTkFrame(parent)
        voice_section.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        voice_section.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            voice_section,
            text="🎤 Voice Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        # TTS Enable
        ctk.CTkLabel(voice_section, text="Text-to-Speech:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.tts_switch = ctk.CTkSwitch(voice_section, text="Enable voice responses")
        self.tts_switch.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Wake Word Enable
        ctk.CTkLabel(voice_section, text="Wake Word:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.wake_word_switch = ctk.CTkSwitch(voice_section, text="Enable wake word detection")
        self.wake_word_switch.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Wake Word Sensitivity
        ctk.CTkLabel(voice_section, text="Wake Word Sensitivity:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.sensitivity_slider = ctk.CTkSlider(voice_section, from_=0.1, to=1.0, number_of_steps=9)
        self.sensitivity_slider.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.sensitivity_slider.set(0.6)
        
        # Theme Settings
        theme_section = ctk.CTkFrame(parent)
        theme_section.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        theme_section.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            theme_section,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        ctk.CTkLabel(theme_section, text="Theme:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_section,
            values=list(ThemeManager.THEMES.keys()),
            command=self._change_theme
        )
        self.theme_menu.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        # Performance Settings
        perf_section = ctk.CTkFrame(parent)
        perf_section.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        perf_section.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            perf_section,
            text="⚡ Performance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        ctk.CTkLabel(perf_section, text="Enable Analytics:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.analytics_switch = ctk.CTkSwitch(perf_section, text="Track usage analytics")
        self.analytics_switch.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(perf_section, text="Performance Monitoring:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.monitoring_switch = ctk.CTkSwitch(perf_section, text="Enable performance monitoring")
        self.monitoring_switch.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Save button
        save_btn = ctk.CTkButton(
            parent,
            text="💾 Save Settings",
            command=self._save_settings,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.grid(row=3, column=0, padx=10, pady=20, sticky="ew")
    
    def _create_help_content(self, parent):
        """Create help content"""
        # Quick Start Guide
        quick_start = ctk.CTkFrame(parent)
        quick_start.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            quick_start,
            text="🚀 Quick Start Guide",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        help_text = """
1. Click "Start Assistant" to begin voice recognition
2. Use wake words: "hey assistant", "computer", "wake up"
3. Speak commands naturally or type them in chat
4. Monitor performance and analytics in dedicated tabs
5. Customize settings to your preferences

Supported Commands:
• "open [app name]" - Launch applications
• "close [app name]" - Close applications  
• "volume up/down" - Control system volume
• "what time is it" - Get current time
• "search for [query]" - Web search
• "set timer for [duration]" - Set countdown timer
• "take screenshot" - Capture screen
• "calculate [expression]" - Math calculations
• And many more...
        """
        
        help_label = ctk.CTkLabel(
            quick_start,
            text=help_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="nw"
        )
        help_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Troubleshooting
        troubleshoot = ctk.CTkFrame(parent)
        troubleshoot.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            troubleshoot,
            text="🔧 Troubleshooting",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        troubleshoot_text = """
Common Issues:

• Microphone not detected: Check audio device settings
• Speech recognition fails: Verify internet connection
• Commands not working: Ensure assistant is started
• Poor accuracy: Adjust wake word sensitivity
• Performance issues: Disable analytics if needed

For more help, check the performance monitor and system logs.
        """
        
        ctk.CTkLabel(
            troubleshoot,
            text=troubleshoot_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="nw"
        ).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
    
    def _setup_themes(self):
        """Setup theme system"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _start_monitoring(self):
        """Start performance monitoring"""
        self.performance_monitor.start_system_monitoring()
        threading.Thread(target=self._update_performance_data, daemon=True).start()
    
    def _update_performance_data(self):
        """Update performance data in background"""
        while True:
            try:
                # Simulate performance data collection
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                self._performance_data["cpu"].append(cpu_percent)
                self._performance_data["memory"].append(memory_percent)
                
                # Keep only last 50 data points
                if len(self._performance_data["cpu"]) > 50:
                    self._performance_data["cpu"].pop(0)
                    self._performance_data["memory"].pop(0)
                
                time.sleep(2)
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(5)
    
    # Navigation methods
    def _show_dashboard(self):
        self._hide_all_views()
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "dashboard"
        self._update_nav_buttons()
    
    def _show_chat(self):
        self._hide_all_views()
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "chat"
        self._update_nav_buttons()
    
    def _show_analytics(self):
        self._hide_all_views()
        self.analytics_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "analytics"
        self._update_nav_buttons()
        self._update_analytics_charts()
    
    def _show_settings(self):
        self._hide_all_views()
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "settings"
        self._update_nav_buttons()
    
    def _show_performance(self):
        self._hide_all_views()
        self.performance_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "performance"
        self._update_nav_buttons()
        self._update_performance_charts()
    
    def _show_help(self):
        self._hide_all_views()
        self.help_frame.grid(row=0, column=0, sticky="nsew")
        self._current_view = "help"
        self._update_nav_buttons()
    
    def _hide_all_views(self):
        """Hide all view frames"""
        for frame in [self.dashboard_frame, self.chat_frame, self.analytics_frame, 
                     self.settings_frame, self.performance_frame, self.help_frame]:
            frame.grid_remove()
    
    def _update_nav_buttons(self):
        """Update navigation button states"""
        for key, btn in self.nav_buttons.items():
            if key == self._current_view:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=("gray85", "gray15"))
    
    # Assistant control methods
    def _start_assistant(self):
        """Start the assistant"""
        success = self._controller.start()
        if success:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.connection_status.configure(text="🟢 Connected")
            self.status_labels["assistant"].configure(text="Assistant: Running")
            self._log_activity("Assistant started successfully")
        else:
            messagebox.showerror("Error", "Failed to start assistant. Check your microphone and settings.")
    
    def _stop_assistant(self):
        """Stop the assistant"""
        self._controller.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.connection_status.configure(text="🔴 Disconnected")
        self.status_labels["assistant"].configure(text="Assistant: Stopped")
        self._log_activity("Assistant stopped")
    
    def _send_chat_message(self, event=None):
        """Send chat message"""
        message = self.chat_entry.get().strip()
        if not message:
            return
        
        if not self._controller.is_running:
            self._add_chat_message("System", "Please start the assistant first.", "system")
            return
        
        self.chat_entry.delete(0, "end")
        self._add_chat_message("You", message, "user")
        self._controller.run_text_command(message)
    
    def _voice_input(self):
        """Handle voice input"""
        if not self._controller.is_running:
            self._add_chat_message("System", "Please start the assistant first.", "system")
            return
        
        self._add_chat_message("System", "Listening for voice input...", "system")
        self._controller.run_voice_command()
    
    def _add_chat_message(self, sender: str, message: str, msg_type: str = "user"):
        """Add message to chat display"""
        message_frame = ctk.CTkFrame(self.chat_display)
        message_frame.grid(row=self._chat_message_count, column=0, sticky="ew", padx=10, pady=5)
        message_frame.grid_columnconfigure(0, weight=1)
        
        # Sender label
        sender_label = ctk.CTkLabel(
            message_frame,
            text=f"{sender} • {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray60", "gray40")
        )
        sender_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Message label
        color_map = {
            "user": ("blue", "lightblue"),
            "assistant": ("green", "lightgreen"),
            "system": ("orange", "yellow")
        }
        
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=color_map.get(msg_type, ("white", "white")),
            wraplength=600,
            justify="left",
            anchor="w"
        )
        message_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self._chat_message_count += 1
        
        # Auto-scroll to bottom
        self.chat_display._parent_canvas.yview_moveto(1.0)
    
    def _log_activity(self, message: str):
        """Log activity to dashboard"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.activity_text.insert("end", log_entry)
        self.activity_text.see("end")
    
    def _update_analytics_charts(self):
        """Update analytics charts"""
        try:
            # Update command frequency chart
            fig, ax, canvas = self.analytics_charts['frequency']
            ax.clear()
            ax.set_facecolor('#2b2b2b')
            ax.set_title("Command Frequency", color='white')
            
            # Sample data - replace with real analytics data
            commands = ['open_app', 'volume', 'search', 'time', 'timer']
            frequencies = [15, 8, 12, 5, 3]
            
            bars = ax.bar(commands, frequencies, color='#3b82f6')
            ax.tick_params(colors='white')
            ax.set_ylabel('Frequency', color='white')
            
            canvas.draw()
            
            # Update response time chart
            fig2, ax2, canvas2 = self.analytics_charts['response_time']
            ax2.clear()
            ax2.set_facecolor('#2b2b2b')
            ax2.set_title("Response Times", color='white')
            
            # Sample response time data
            times = list(range(1, 21))
            response_times = np.random.normal(200, 50, 20)  # Sample data
            
            ax2.plot(times, response_times, color='#10b981', linewidth=2)
            ax2.tick_params(colors='white')
            ax2.set_ylabel('Response Time (ms)', color='white')
            ax2.set_xlabel('Request #', color='white')
            
            canvas2.draw()
            
        except Exception as e:
            print(f"Error updating analytics charts: {e}")
    
    def _update_performance_charts(self):
        """Update performance charts"""
        try:
            # Update CPU chart
            fig, ax, canvas = self.performance_charts['cpu']
            ax.clear()
            ax.set_facecolor('#2b2b2b')
            ax.set_title("CPU Usage", color='white')
            ax.set_ylim(0, 100)
            
            if self._performance_data["cpu"]:
                times = list(range(len(self._performance_data["cpu"])))
                ax.plot(times, self._performance_data["cpu"], color='#ef4444', linewidth=2)
                ax.fill_between(times, self._performance_data["cpu"], alpha=0.3, color='#ef4444')
            
            ax.tick_params(colors='white')
            ax.set_ylabel('CPU %', color='white')
            
            canvas.draw()
            
            # Update Memory chart
            fig2, ax2, canvas2 = self.performance_charts['memory']
            ax2.clear()
            ax2.set_facecolor('#2b2b2b')
            ax2.set_title("Memory Usage", color='white')
            
            if self._performance_data["memory"]:
                times = list(range(len(self._performance_data["memory"])))
                ax2.plot(times, self._performance_data["memory"], color='#f59e0b', linewidth=2)
                ax2.fill_between(times, self._performance_data["memory"], alpha=0.3, color='#f59e0b')
            
            ax2.tick_params(colors='white')
            ax2.set_ylabel('Memory %', color='white')
            
            canvas2.draw()
            
        except Exception as e:
            print(f"Error updating performance charts: {e}")
    
    def _change_theme(self, theme_name: str):
        """Change UI theme"""
        self.theme_manager.set_theme(theme_name)
        # You would implement theme application logic here
    
    def _save_settings(self):
        """Save settings"""
        settings = {
            "tts_enabled": self.tts_switch.get(),
            "wake_word_enabled": self.wake_word_switch.get(),
            "wake_word_sensitivity": self.sensitivity_slider.get(),
            "theme": self.theme_menu.get(),
            "analytics_enabled": self.analytics_switch.get(),
            "monitoring_enabled": self.monitoring_switch.get()
        }
        
        # Save to file
        try:
            with open("config/ui_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _update_ui(self):
        """Update UI with data from queue"""
        try:
            while True:
                kind, payload = self._ui_queue.get_nowait()
                
                if kind == "log":
                    self._log_activity(str(payload))
                    if self._current_view == "chat":
                        self._add_chat_message("Assistant", str(payload), "assistant")
                
                elif kind == "status":
                    self.status_text.configure(text=str(payload))
                    if "Wake word" in str(payload):
                        self.status_labels["wake_word"].configure(text=str(payload))
                
                elif kind == "intent" and isinstance(payload, Intent):
                    intent_text = f"Intent: {payload.type.value} (confidence: {payload.confidence:.2f})"
                    self._log_activity(intent_text)
                
                elif kind == "result" and isinstance(payload, dict):
                    result_msg = payload.get("message", "")
                    if result_msg:
                        self._log_activity(f"Result: {result_msg}")
                        if self._current_view == "chat":
                            self._add_chat_message("Assistant", result_msg, "assistant")
        
        except queue.Empty:
            pass
        
        # Update statistics
        self._update_statistics()
        
        # Schedule next update
        self.after(100, self._update_ui)
    
    def _update_statistics(self):
        """Update dashboard statistics"""
        try:
            # Update command count
            command_count = len(self._command_history)
            self.stats_cards["commands"].value_label.configure(text=str(command_count))
            
            # Update uptime (if assistant is running)
            if self._controller.is_running:
                # Calculate uptime - you'd track start time
                uptime = "01:23:45"  # Placeholder
                self.stats_cards["uptime"].value_label.configure(text=uptime)
            
            # Update accuracy (placeholder)
            accuracy = "95%"
            self.stats_cards["accuracy"].value_label.configure(text=accuracy)
            
            # Update response time (placeholder)
            if self._performance_data["response_times"]:
                avg_response = f"{np.mean(self._performance_data['response_times']):.0f}ms"
            else:
                avg_response = "0ms"
            self.stats_cards["response"].value_label.configure(text=avg_response)
            
        except Exception as e:
            print(f"Error updating statistics: {e}")


def main():
    """Main entry point"""
    app = ProfessionalAssistantUI()
    app.mainloop()


if __name__ == "__main__":
    main()