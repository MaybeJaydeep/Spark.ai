#!/usr/bin/env python3
"""
Exceptional UI Launcher for AI Voice Assistant

Launches the world-class exceptional interface with:
- Stunning visual design with perfect typography
- Seamless theme switching with live updates
- Advanced animations and micro-interactions
- Professional data visualizations
- Accessibility excellence (WCAG 2.1 AAA)
- Responsive design with fluid layouts
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/exceptional_ui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'customtkinter',
        'matplotlib',
        'numpy',
        'psutil',
        'PIL'  # Pillow
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    return True


def setup_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'config/themes',
        'data',
        'analytics'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def print_banner():
    """Print exceptional UI banner"""
    print("\n" + "="*80)
    print("✨ SPARK AI ASSISTANT - EXCEPTIONAL PROFESSIONAL UI")
    print("="*80)
    print("\n🎨 World-Class Interface Features:")
    print("   • Stunning visual design with perfect typography")
    print("   • Seamless theme switching with live updates")
    print("   • Advanced animations and micro-interactions")
    print("   • Professional data visualizations")
    print("   • Accessibility excellence (WCAG 2.1 AAA)")
    print("   • Responsive design with fluid layouts")
    print("   • 6 professional themes with custom creation")
    print("   • Real-time performance monitoring")
    print("   • Advanced component system")
    print("\n🚀 Ready to launch exceptional experience...")
    print("="*80)


def main():
    """Main entry point for exceptional UI"""
    print_banner()
    
    logger.info("Starting Exceptional AI Assistant UI...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    try:
        # Import and launch exceptional UI
        from ui.exceptional_ui import ExceptionalUI
        
        logger.info("Launching exceptional interface...")
        app = ExceptionalUI()
        
        # Start the application
        app.mainloop()
        
    except ImportError as e:
        logger.error(f"Failed to import exceptional UI components: {e}")
        logger.error("Make sure all dependencies are installed correctly")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("Exceptional UI session ended")


if __name__ == "__main__":
    main()