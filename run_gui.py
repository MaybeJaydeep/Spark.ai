#!/usr/bin/env python3
"""
GUI Launcher for AI Assistant

Quick launcher script to start the assistant with GUI.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    # Force GUI mode
    sys.argv.append('--gui')
    main()
