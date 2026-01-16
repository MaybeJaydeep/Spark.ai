#!/usr/bin/env python3
"""
Integration Test - Test complete pipeline
"""

import logging
from nlp.intent_parser import IntentParser
from toc.dispatcher import CommandDispatcher

def test_pipeline():
    """Test the complete command pipeline"""
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("🧪 INTEGRATION TEST - Command Pipeline")
    print("="*60)
    print()
    
    # Initialize components
    print("Initializing components...")
    parser = IntentParser()
    dispatcher = CommandDispatcher()
    print("✅ Components initialized")
    print()
    
    # Test commands
    test_commands = [
        "open firefox",
        "what time is it",
        "volume up",
        "search for python",
        "mute",
        "set timer for 5 minutes",
        "take a screenshot",
        "close firefox"
    ]
    
    results = []
    
    for command in test_commands:
        print(f"Testing: '{command}'")
        print("-" * 40)
        
        # Parse intent
        intent = parser.parse(command)
        print(f"  Intent: {intent.type.value}")
        print(f"  Confidence: {intent.confidence:.2f}")
        
        if intent.entities:
            print(f"  Entities:")
            for entity in intent.entities:
                print(f"    - {entity.type}: '{entity.value}'")
        
        # Execute command
        result = dispatcher.dispatch(intent)
        print(f"  Result: {result['message']}")
        print(f"  Success: {'✅' if result['success'] else '❌'}")
        
        results.append({
            'command': command,
            'success': result['success']
        })
        
        print()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Total commands: {total}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total - success_count}")
    print(f"Success rate: {success_count/total*100:.1f}%")
    print()
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['command']}")
    
    print()
    print("="*60)


if __name__ == "__main__":
    test_pipeline()
