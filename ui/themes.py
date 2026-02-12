#!/usr/bin/env python3
"""
Professional Theme System for AI Assistant UI

Provides comprehensive theming with:
- Multiple professional color schemes
- Dynamic theme switching
- Accessibility compliance
- Custom component styling
- Export/import theme configurations
"""

import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import customtkinter as ctk


@dataclass
class ColorPalette:
    """Color palette for UI theming"""
    # Primary colors
    primary: str
    primary_dark: str
    primary_light: str
    
    # Secondary colors
    secondary: str
    secondary_dark: str
    secondary_light: str
    
    # Accent colors
    accent: str
    accent_dark: str
    accent_light: str
    
    # Background colors
    background: str
    surface: str
    card: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Interactive colors
    hover: str
    pressed: str
    selected: str
    focus: str


@dataclass
class Typography:
    """Typography settings"""
    font_family: str
    font_size_small: int
    font_size_normal: int
    font_size_large: int
    font_size_xlarge: int
    font_weight_normal: str
    font_weight_bold: str
    line_height: float


@dataclass
class Spacing:
    """Spacing and sizing settings"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48
    
    # Component sizes
    button_height: int = 40
    input_height: int = 36
    card_padding: int = 20
    section_padding: int = 24


@dataclass
class Theme:
    """Complete theme configuration"""
    name: str
    display_name: str
    colors: ColorPalette
    typography: Typography
    spacing: Spacing
    is_dark: bool
    accessibility_compliant: bool = True


class ThemeManager:
    """Professional theme management system"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.theme_dir = Path("config/themes")
        self.theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Load built-in themes
        self._load_builtin_themes()
        
        # Load custom themes
        self._load_custom_themes()
        
        # Set default theme
        self.set_theme("dark_professional")
    
    def _load_builtin_themes(self):
        """Load built-in professional themes"""
        
        # Dark Professional Theme
        dark_professional = Theme(
            name="dark_professional",
            display_name="Dark Professional",
            is_dark=True,
            colors=ColorPalette(
                primary="#1e293b",
                primary_dark="#0f172a",
                primary_light="#334155",
                secondary="#475569",
                secondary_dark="#334155",
                secondary_light="#64748b",
                accent="#3b82f6",
                accent_dark="#2563eb",
                accent_light="#60a5fa",
                background="#0f172a",
                surface="#1e293b",
                card="#334155",
                text_primary="#f8fafc",
                text_secondary="#cbd5e1",
                text_disabled="#64748b",
                success="#10b981",
                warning="#f59e0b",
                error="#ef4444",
                info="#06b6d4",
                hover="#475569",
                pressed="#334155",
                selected="#3b82f6",
                focus="#60a5fa"
            ),
            typography=Typography(
                font_family="Segoe UI",
                font_size_small=11,
                font_size_normal=13,
                font_size_large=16,
                font_size_xlarge=20,
                font_weight_normal="normal",
                font_weight_bold="bold",
                line_height=1.4
            ),
            spacing=Spacing()
        )
        
        # Light Professional Theme
        light_professional = Theme(
            name="light_professional",
            display_name="Light Professional",
            is_dark=False,
            colors=ColorPalette(
                primary="#ffffff",
                primary_dark="#f8fafc",
                primary_light="#ffffff",
                secondary="#f1f5f9",
                secondary_dark="#e2e8f0",
                secondary_light="#f8fafc",
                accent="#3b82f6",
                accent_dark="#2563eb",
                accent_light="#60a5fa",
                background="#f8fafc",
                surface="#ffffff",
                card="#f1f5f9",
                text_primary="#1e293b",
                text_secondary="#475569",
                text_disabled="#94a3b8",
                success="#059669",
                warning="#d97706",
                error="#dc2626",
                info="#0891b2",
                hover="#f1f5f9",
                pressed="#e2e8f0",
                selected="#3b82f6",
                focus="#60a5fa"
            ),
            typography=Typography(
                font_family="Segoe UI",
                font_size_small=11,
                font_size_normal=13,
                font_size_large=16,
                font_size_xlarge=20,
                font_weight_normal="normal",
                font_weight_bold="bold",
                line_height=1.4
            ),
            spacing=Spacing()
        )
        
        # Blue Corporate Theme
        blue_corporate = Theme(
            name="blue_corporate",
            display_name="Blue Corporate",
            is_dark=False,
            colors=ColorPalette(
                primary="#1e40af",
                primary_dark="#1e3a8a",
                primary_light="#3b82f6",
                secondary="#dbeafe",
                secondary_dark="#bfdbfe",
                secondary_light="#eff6ff",
                accent="#60a5fa",
                accent_dark="#3b82f6",
                accent_light="#93c5fd",
                background="#eff6ff",
                surface="#ffffff",
                card="#dbeafe",
                text_primary="#1e3a8a",
                text_secondary="#3730a3",
                text_disabled="#6b7280",
                success="#059669",
                warning="#d97706",
                error="#dc2626",
                info="#0891b2",
                hover="#dbeafe",
                pressed="#bfdbfe",
                selected="#3b82f6",
                focus="#60a5fa"
            ),
            typography=Typography(
                font_family="Segoe UI",
                font_size_small=11,
                font_size_normal=13,
                font_size_large=16,
                font_size_xlarge=20,
                font_weight_normal="normal",
                font_weight_bold="bold",
                line_height=1.4
            ),
            spacing=Spacing()
        )
        
        # High Contrast Theme (Accessibility)
        high_contrast = Theme(
            name="high_contrast",
            display_name="High Contrast",
            is_dark=True,
            accessibility_compliant=True,
            colors=ColorPalette(
                primary="#000000",
                primary_dark="#000000",
                primary_light="#1a1a1a",
                secondary="#333333",
                secondary_dark="#1a1a1a",
                secondary_light="#4d4d4d",
                accent="#00ff00",
                accent_dark="#00cc00",
                accent_light="#33ff33",
                background="#000000",
                surface="#1a1a1a",
                card="#333333",
                text_primary="#ffffff",
                text_secondary="#cccccc",
                text_disabled="#666666",
                success="#00ff00",
                warning="#ffff00",
                error="#ff0000",
                info="#00ffff",
                hover="#333333",
                pressed="#1a1a1a",
                selected="#00ff00",
                focus="#ffff00"
            ),
            typography=Typography(
                font_family="Segoe UI",
                font_size_small=12,
                font_size_normal=14,
                font_size_large=18,
                font_size_xlarge=22,
                font_weight_normal="normal",
                font_weight_bold="bold",
                line_height=1.5
            ),
            spacing=Spacing(
                # Larger spacing for accessibility
                xs=6, sm=12, md=20, lg=28, xl=36, xxl=52,
                button_height=44, input_height=40
            )
        )
        
        # Register themes
        self.themes.update({
            "dark_professional": dark_professional,
            "light_professional": light_professional,
            "blue_corporate": blue_corporate,
            "high_contrast": high_contrast
        })
    
    def _load_custom_themes(self):
        """Load custom themes from files"""
        for theme_file in self.theme_dir.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                
                theme = self._dict_to_theme(theme_data)
                self.themes[theme.name] = theme
                
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def _dict_to_theme(self, data: Dict[str, Any]) -> Theme:
        """Convert dictionary to Theme object"""
        colors = ColorPalette(**data['colors'])
        typography = Typography(**data['typography'])
        spacing = Spacing(**data['spacing'])
        
        return Theme(
            name=data['name'],
            display_name=data['display_name'],
            colors=colors,
            typography=typography,
            spacing=spacing,
            is_dark=data['is_dark'],
            accessibility_compliant=data.get('accessibility_compliant', True)
        )
    
    def _theme_to_dict(self, theme: Theme) -> Dict[str, Any]:
        """Convert Theme object to dictionary"""
        return {
            'name': theme.name,
            'display_name': theme.display_name,
            'colors': asdict(theme.colors),
            'typography': asdict(theme.typography),
            'spacing': asdict(theme.spacing),
            'is_dark': theme.is_dark,
            'accessibility_compliant': theme.accessibility_compliant
        }
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available themes as name -> display_name mapping"""
        return {name: theme.display_name for name, theme in self.themes.items()}
    
    def set_theme(self, theme_name: str) -> bool:
        """Set current theme"""
        if theme_name not in self.themes:
            return False
        
        self.current_theme = self.themes[theme_name]
        
        # Apply to CustomTkinter
        ctk.set_appearance_mode("dark" if self.current_theme.is_dark else "light")
        
        # Set custom color theme
        self._apply_ctk_theme()
        
        return True
    
    def _apply_ctk_theme(self):
        """Apply theme to CustomTkinter"""
        if not self.current_theme:
            return
        
        # Create custom color theme for CustomTkinter
        theme_dict = {
            "CTk": {
                "fg_color": [self.current_theme.colors.background, self.current_theme.colors.background]
            },
            "CTkToplevel": {
                "fg_color": [self.current_theme.colors.background, self.current_theme.colors.background]
            },
            "CTkFrame": {
                "corner_radius": 8,
                "border_width": 0,
                "fg_color": [self.current_theme.colors.surface, self.current_theme.colors.surface],
                "top_fg_color": [self.current_theme.colors.card, self.current_theme.colors.card]
            },
            "CTkButton": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": [self.current_theme.colors.accent, self.current_theme.colors.accent],
                "hover_color": [self.current_theme.colors.accent_dark, self.current_theme.colors.accent_dark],
                "border_color": [self.current_theme.colors.accent, self.current_theme.colors.accent],
                "text_color": [self.current_theme.colors.text_primary, self.current_theme.colors.text_primary],
                "text_color_disabled": [self.current_theme.colors.text_disabled, self.current_theme.colors.text_disabled]
            },
            "CTkLabel": {
                "corner_radius": 0,
                "fg_color": "transparent",
                "text_color": [self.current_theme.colors.text_primary, self.current_theme.colors.text_primary]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 2,
                "fg_color": [self.current_theme.colors.surface, self.current_theme.colors.surface],
                "border_color": [self.current_theme.colors.secondary, self.current_theme.colors.secondary],
                "text_color": [self.current_theme.colors.text_primary, self.current_theme.colors.text_primary],
                "placeholder_text_color": [self.current_theme.colors.text_secondary, self.current_theme.colors.text_secondary]
            },
            "CTkTextbox": {
                "corner_radius": 6,
                "border_width": 0,
                "fg_color": [self.current_theme.colors.surface, self.current_theme.colors.surface],
                "border_color": [self.current_theme.colors.secondary, self.current_theme.colors.secondary],
                "text_color": [self.current_theme.colors.text_primary, self.current_theme.colors.text_primary],
                "scrollbar_button_color": [self.current_theme.colors.secondary, self.current_theme.colors.secondary],
                "scrollbar_button_hover_color": [self.current_theme.colors.hover, self.current_theme.colors.hover]
            }
        }
        
        # Apply the theme (this would require CustomTkinter theme system integration)
        # For now, we'll store it for manual application
        self._ctk_theme = theme_dict
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get current theme"""
        return self.current_theme
    
    def save_theme(self, theme: Theme) -> bool:
        """Save custom theme to file"""
        try:
            theme_file = self.theme_dir / f"{theme.name}.json"
            with open(theme_file, 'w') as f:
                json.dump(self._theme_to_dict(theme), f, indent=2)
            
            self.themes[theme.name] = theme
            return True
            
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete custom theme"""
        if theme_name not in self.themes:
            return False
        
        # Don't delete built-in themes
        builtin_themes = ["dark_professional", "light_professional", "blue_corporate", "high_contrast"]
        if theme_name in builtin_themes:
            return False
        
        try:
            theme_file = self.theme_dir / f"{theme_name}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            del self.themes[theme_name]
            return True
            
        except Exception as e:
            print(f"Error deleting theme: {e}")
            return False
    
    def export_theme(self, theme_name: str, export_path: str) -> bool:
        """Export theme to file"""
        if theme_name not in self.themes:
            return False
        
        try:
            theme = self.themes[theme_name]
            with open(export_path, 'w') as f:
                json.dump(self._theme_to_dict(theme), f, indent=2)
            return True
            
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, import_path: str) -> bool:
        """Import theme from file"""
        try:
            with open(import_path, 'r') as f:
                theme_data = json.load(f)
            
            theme = self._dict_to_theme(theme_data)
            self.themes[theme.name] = theme
            
            # Save to themes directory
            self.save_theme(theme)
            return True
            
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False
    
    def create_custom_theme(self, base_theme_name: str, new_name: str, 
                          modifications: Dict[str, Any]) -> Optional[Theme]:
        """Create custom theme based on existing theme"""
        if base_theme_name not in self.themes:
            return None
        
        base_theme = self.themes[base_theme_name]
        
        # Create copy of base theme
        theme_dict = self._theme_to_dict(base_theme)
        theme_dict['name'] = new_name
        theme_dict['display_name'] = modifications.get('display_name', new_name.replace('_', ' ').title())
        
        # Apply modifications
        for key, value in modifications.items():
            if key in theme_dict:
                if isinstance(theme_dict[key], dict) and isinstance(value, dict):
                    theme_dict[key].update(value)
                else:
                    theme_dict[key] = value
        
        # Create new theme
        new_theme = self._dict_to_theme(theme_dict)
        self.themes[new_name] = new_theme
        
        return new_theme
    
    def get_color(self, color_name: str) -> str:
        """Get color from current theme"""
        if not self.current_theme:
            return "#000000"
        
        return getattr(self.current_theme.colors, color_name, "#000000")
    
    def get_font(self, size: str = "normal", weight: str = "normal") -> Tuple[str, int, str]:
        """Get font configuration from current theme"""
        if not self.current_theme:
            return ("Segoe UI", 13, "normal")
        
        typography = self.current_theme.typography
        
        size_map = {
            "small": typography.font_size_small,
            "normal": typography.font_size_normal,
            "large": typography.font_size_large,
            "xlarge": typography.font_size_xlarge
        }
        
        weight_map = {
            "normal": typography.font_weight_normal,
            "bold": typography.font_weight_bold
        }
        
        return (
            typography.font_family,
            size_map.get(size, typography.font_size_normal),
            weight_map.get(weight, typography.font_weight_normal)
        )
    
    def get_spacing(self, size: str) -> int:
        """Get spacing value from current theme"""
        if not self.current_theme:
            return 16
        
        return getattr(self.current_theme.spacing, size, 16)


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    return theme_manager