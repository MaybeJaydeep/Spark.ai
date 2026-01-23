#!/usr/bin/env python3
"""
Windows Startup Installer for AI Assistant

Creates a small .bat file in the user's Startup folder so that the
hands-free wake-word assistant starts automatically when Windows logs in.

Usage:
    python install_startup.py
"""

import os
import sys
import platform
from pathlib import Path


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def get_startup_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found.")
    return Path(appdata) / r"Microsoft\Windows\Start Menu\Programs\Startup"


def main() -> None:
    if not is_windows():
        print("This startup installer only supports Windows.")
        return

    startup_dir = get_startup_dir()
    startup_dir.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).resolve().parent
    python_exe = Path(sys.executable).resolve()

    # We use the hands-free assistant so it can run without opening a GUI
    target_script = project_root / "voice_assistant_handsfree.py"

    if not target_script.exists():
        raise FileNotFoundError(f"Could not find {target_script}")

    batch_path = startup_dir / "AI_Assistant_Handsfree.bat"

    # Create a simple batch file that cd's into the project and runs the assistant
    lines = [
        "@echo off",
        f'cd /d "{project_root}"',
        f'"{python_exe}" "{target_script.name}" --no-tts',
    ]

    batch_path.write_text("\n".join(lines), encoding="utf-8")

    print("✅ Startup entry created for AI Assistant (hands-free mode).")
    print(f"   File: {batch_path}")
    print("ℹ️  It will start automatically the next time you log in to Windows.")


if __name__ == "__main__":
    main()

