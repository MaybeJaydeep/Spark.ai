#!/usr/bin/env python3
"""
Setup script for AI Assistant Wake Word Detection
"""

import subprocess
import sys
import os
import platform


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def install_system_dependencies():
    """Install system-level dependencies based on OS"""
    system = platform.system().lower()
    
    print(f"🔧 Detected OS: {system}")
    
    if system == "linux":
        print("📦 Installing Linux audio dependencies...")
        try:
            # Ubuntu/Debian
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True)
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "portaudio19-dev", "python3-pyaudio", "alsa-utils"
            ], check=True)
            print("✅ Linux dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install system dependencies. You may need to install them manually:")
            print("   sudo apt-get install portaudio19-dev python3-pyaudio alsa-utils")
    
    elif system == "darwin":  # macOS
        print("📦 Installing macOS audio dependencies...")
        try:
            # Check if Homebrew is available
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            subprocess.run(["brew", "install", "portaudio"], check=True)
            print("✅ macOS dependencies installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Homebrew not found. Please install PortAudio manually:")
            print("   brew install portaudio")
    
    elif system == "windows":
        print("📦 Windows detected - PyAudio should install from pip")
        print("✅ No additional system dependencies needed")
    
    else:
        print(f"⚠️  Unknown OS: {system}. You may need to install audio dependencies manually")


def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        print("💡 Try installing manually with: pip install -r requirements.txt")
        return False


def create_config_directory():
    """Create configuration directory if it doesn't exist"""
    config_dir = "config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"✅ Created {config_dir} directory")
    else:
        print(f"✅ {config_dir} directory already exists")


def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import numpy
        import webrtcvad
        import sounddevice
        import soundfile
        print("✅ All required modules can be imported")

        # Test audio device access via sounddevice
        try:
            devices = sounddevice.query_devices()
            input_devices = [d for d in devices if d.get("max_input_channels", 0) > 0]
            print(f"✅ Found {len(devices)} audio devices ({len(input_devices)} inputs)")
            if input_devices:
                print("✅ Example input devices:")
                for d in input_devices[:3]:
                    print(f"   • {d.get('name')}")
            else:
                print("⚠️  No audio input devices found")
        except Exception as e:
            print(f"⚠️  Could not query audio devices: {e}")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 AI Assistant Wake Word Detection Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create config directory
    create_config_directory()
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed due to dependency installation issues")
        sys.exit(1)
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run: python main.py")
        print("   2. Speak a wake word: 'hey assistant', 'computer', or 'wake up'")
        print("   3. Check config/wake_word_config.json to customize settings")
    else:
        print("\n⚠️  Setup completed with warnings. Some features may not work.")
        print("💡 Try running: python main.py")


if __name__ == "__main__":
    main()