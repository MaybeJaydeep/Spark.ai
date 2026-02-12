#!/usr/bin/env python3
"""
AI Assistant Launcher

Easy launcher for the AI assistant with different modes.
"""

import sys
import os

def print_menu():
    """Display menu"""
    print("\n" + "="*60)
    print("🤖 AI ASSISTANT - UNIFIED INTERFACE")
    print("="*60)
    print("\nChoose a mode:")
    print()
    print("1. 🎨 Unified Interface (Recommended)")
    print("   - Exceptional UI with all features")
    print("   - Voice and text input")
    print("   - 6 professional themes")
    print()
    print("2. 🙌 Hands-Free Mode")
    print("   - Say wake word to activate")
    print("   - No button press needed")
    print("   - True voice assistant")
    print()
    print("3. ⌨️  Text Mode")
    print("   - Type commands")
    print("   - No microphone needed")
    print("   - Fast testing")
    print()
    print("4. 🧪 Test Voice Input")
    print("   - Test microphone")
    print("   - Single command test")
    print()
    print("5. 📊 Check System")
    print("   - Test all components")
    print("   - Check dependencies")
    print()
    print("0. ❌ Exit")
    print()


def main():
    """Main launcher"""
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            elif choice == '1':
                print("\n🚀 Starting Unified Interface...")
                print("="*60)
                os.system("python main.py")
            
            elif choice == '2':
                print("\n🚀 Starting Hands-Free Mode...")
                print("="*60)
                os.system("python voice_assistant_handsfree.py")
            
            elif choice == '3':
                print("\n🚀 Starting Text Mode...")
                print("="*60)
                os.system("python test_assistant.py")
            
            elif choice == '4':
                print("\n🚀 Testing Voice Input...")
                print("="*60)
                os.system("python test_voice.py")
            
            elif choice == '5':
                print("\n🚀 Checking System...")
                print("="*60)
                os.system("python test_microphone.py")
            
            else:
                print("\n❌ Invalid choice. Please enter 0-5.")
                continue
            
            # Wait for user
            input("\n\nPress ENTER to return to menu...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress ENTER to continue...")


if __name__ == "__main__":
    main()
