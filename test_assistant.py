#!/usr/bin/env python3
"""
Text-based Assistant Tester

Test the assistant by typing commands instead of speaking them.
This allows testing without microphone/audio hardware.
"""

import logging
from nlp.intent_parser import IntentParser, IntentType
from actions.apps import AppController

def main():
    """Main test loop"""
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("🤖 AI ASSISTANT - TEXT MODE TESTER")
    print("="*60)
    print("\n💡 Type commands to test the assistant")
    print("   Examples:")
    print("   - open firefox")
    print("   - open chrome")
    print("   - search for python tutorials")
    print("   - what time is it")
    print("   - volume up")
    print("   - take a screenshot")
    print("\n   Type 'quit' or 'exit' to stop\n")
    print("-"*60)
    
    # Initialize components
    parser = IntentParser()
    app_controller = AppController()
    
    while True:
        try:
            # Get user input
            command = input("\n🎤 You: ").strip()
            
            if not command:
                continue
            
            # Check for exit commands
            if command.lower() in ['quit', 'exit', 'bye', 'stop']:
                print("\n👋 Goodbye!")
                break
            
            # Parse the command
            print(f"\n📝 Processing: '{command}'")
            intent = parser.parse(command)
            
            # Display parsed intent
            print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
            
            if intent.entities:
                print(f"📦 Entities:")
                for entity in intent.entities:
                    print(f"   - {entity.type}: '{entity.value}'")
            
            # Execute the action
            print(f"\n🚀 Executing action...")
            execute_action(intent, app_controller)
            
            print("-"*60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logging.exception("Error processing command")


def execute_action(intent, app_controller):
    """Execute action based on intent"""
    
    if intent.type == IntentType.OPEN_APP:
        app_entity = intent.get_entity("app_name")
        if app_entity:
            app_name = app_entity.value
            print(f"   Opening {app_name}...")
            success = app_controller.open_app(app_name)
            if success:
                print(f"   ✅ {app_name} opened successfully!")
            else:
                print(f"   ❌ Failed to open {app_name}")
        else:
            print("   ❌ No app name specified")
    
    elif intent.type == IntentType.CLOSE_APP:
        app_entity = intent.get_entity("app_name")
        if app_entity:
            app_name = app_entity.value
            print(f"   Closing {app_name}...")
            success = app_controller.close_app(app_name)
            if success:
                print(f"   ✅ {app_name} closed successfully!")
            else:
                print(f"   ❌ Failed to close {app_name}")
        else:
            print("   ❌ No app name specified")
    
    elif intent.type == IntentType.SEARCH:
        query_entity = intent.get_entity("query")
        if query_entity:
            query = query_entity.value
            print(f"   Searching for: {query}")
            success = app_controller.search_web(query)
            if success:
                print(f"   ✅ Search opened in browser!")
            else:
                print(f"   ❌ Failed to open search")
        else:
            print("   ❌ No search query specified")
    
    elif intent.type == IntentType.TAKE_SCREENSHOT:
        print(f"   Taking screenshot...")
        # TODO: Implement screenshot functionality
        print(f"   ⚠️  Screenshot functionality not yet implemented")
    
    elif intent.type == IntentType.GET_TIME:
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        print(f"   🕐 The time is {current_time}")
    
    elif intent.type == IntentType.VOLUME_UP:
        print(f"   🔊 Increasing volume...")
        print(f"   ⚠️  Volume control not yet implemented")
    
    elif intent.type == IntentType.VOLUME_DOWN:
        print(f"   🔉 Decreasing volume...")
        print(f"   ⚠️  Volume control not yet implemented")
    
    elif intent.type == IntentType.SHUTDOWN:
        print(f"   ⚠️  Shutdown command detected (not executing for safety)")
    
    elif intent.type == IntentType.UNKNOWN:
        print(f"   ❓ I didn't understand that command")
        print(f"   💡 Try commands like 'open firefox' or 'search for cats'")
    
    else:
        print(f"   ⚠️  Action for '{intent.type.value}' not yet implemented")


if __name__ == "__main__":
    main()
