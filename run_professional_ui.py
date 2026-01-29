#!/usr/bin/env python3
"""
Professional UI Launcher for AI Voice Assistant

Launches the industry-level professional interface with:
- Multi-panel dashboard
- Real-time analytics
- Advanced configuration
- Performance monitoring
- Professional styling
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
        logging.FileHandler('logs/professional_ui.log'),
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


def main():
    """Main entry point for professional UI"""
    logger.info("Starting Professional AI Assistant UI...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    try:
        # Import and launch professional UI
        from ui.professional_app import ProfessionalAssistantUI
        
        logger.info("Launching professional interface...")
        app = ProfessionalAssistantUI()
        
        # Start the application
        app.mainloop()
        
    except ImportError as e:
        logger.error(f"Failed to import professional UI components: {e}")
        logger.error("Make sure all dependencies are installed correctly")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("Professional UI session ended")


if __name__ == "__main__":
    main()