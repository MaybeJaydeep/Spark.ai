"""
Intent Parser Module

Parses natural language text to extract user intents and entities.
"""

import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Supported intent types"""
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SEARCH = "search"
    PLAY_MUSIC = "play_music"
    SET_TIMER = "set_timer"
    GET_WEATHER = "get_weather"
    GET_TIME = "get_time"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    SHUTDOWN = "shutdown"
    TAKE_SCREENSHOT = "take_screenshot"
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """Extracted entity from text"""
    type: str
    value: str
    confidence: float


@dataclass
class Intent:
    """Parsed intent with entities"""
    type: IntentType
    confidence: float
    text: str
    entities: List[Entity]
    raw_text: str
    
    def get_entity(self, entity_type: str) -> Optional[Entity]:
        """Get first entity of specified type"""
        for entity in self.entities:
            if entity.type == entity_type:
                return entity
        return None


class IntentParser:
    """
    Natural Language Intent Parser
    
    Analyzes text to determine user intent and extract relevant entities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, Any]:
        """Initialize intent patterns"""
        return {
            IntentType.OPEN_APP.value: {
                "keywords": ["open", "launch", "start"],
                "patterns": [r"(?:open|launch|start)\s+(.+)"],
                "entity_types": ["app_name"]
            },
            IntentType.CLOSE_APP.value: {
                "keywords": ["close", "quit", "exit"],
                "patterns": [r"(?:close|quit|exit)\s+(.+)"],
                "entity_types": ["app_name"]
            },
            IntentType.SEARCH.value: {
                "keywords": ["search", "find", "google"],
                "patterns": [r"(?:search|find|google)\s+(?:for\s+)?(.+)"],
                "entity_types": ["query"]
            },
            IntentType.PLAY_MUSIC.value: {
                "keywords": ["play", "music"],
                "patterns": [r"play\s+(.+)"],
                "entity_types": ["song_name"]
            },
            IntentType.SET_TIMER.value: {
                "keywords": ["timer", "set timer"],
                "patterns": [r"timer\s+for\s+(\d+)\s*(minutes?|seconds?)"],
                "entity_types": ["duration", "unit"]
            },
            IntentType.GET_WEATHER.value: {
                "keywords": ["weather", "temperature"],
                "patterns": [r"weather(?:\s+in\s+(.+))?"],
                "entity_types": ["location"]
            },
            IntentType.GET_TIME.value: {
                "keywords": ["time", "what time"],
                "patterns": [r"(?:what's|what is)\s+the\s+time"],
                "entity_types": []
            },
            IntentType.VOLUME_UP.value: {
                "keywords": ["volume up", "louder"],
                "patterns": [r"volume\s+up"],
                "entity_types": []
            },
            IntentType.VOLUME_DOWN.value: {
                "keywords": ["volume down", "quieter"],
                "patterns": [r"volume\s+down"],
                "entity_types": []
            },
            IntentType.SHUTDOWN.value: {
                "keywords": ["shutdown", "shut down"],
                "patterns": [r"shut\s*down"],
                "entity_types": []
            },
            IntentType.TAKE_SCREENSHOT.value: {
                "keywords": ["screenshot", "screen capture"],
                "patterns": [r"(?:take|capture)\s+(?:a\s+)?screenshot"],
                "entity_types": []
            },
        }
    
    def parse(self, text: str) -> Intent:
        """Parse text to extract intent and entities"""
        if not text or not text.strip():
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                text="",
                entities=[],
                raw_text=text
            )
        
        normalized_text = text.lower().strip()
        
        best_intent = None
        best_confidence = 0.0
        best_entities = []
        
        for intent_name, pattern_data in self.patterns.items():
            keyword_match = self._check_keywords(normalized_text, pattern_data["keywords"])
            
            if keyword_match:
                entities, confidence = self._extract_entities(
                    normalized_text,
                    pattern_data["patterns"],
                    pattern_data["entity_types"]
                )
                
                total_confidence = (keyword_match + confidence) / 2
                
                if total_confidence > best_confidence:
                    best_confidence = total_confidence
                    best_intent = intent_name
                    best_entities = entities
        
        if best_intent:
            intent_type = IntentType(best_intent)
        else:
            intent_type = IntentType.UNKNOWN
            best_confidence = 0.0
        
        return Intent(
            type=intent_type,
            confidence=best_confidence,
            text=normalized_text,
            entities=best_entities,
            raw_text=text
        )
    
    def _check_keywords(self, text: str, keywords: List[str]) -> float:
        """Check if keywords are present"""
        matches = sum(1 for kw in keywords if kw.lower() in text)
        return min(1.0, matches / max(1, len(keywords)))
    
    def _extract_entities(self, text: str, patterns: List[str], 
                         entity_types: List[str]) -> Tuple[List[Entity], float]:
        """Extract entities using regex"""
        entities = []
        confidence = 0.0
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                confidence = 0.9
                for i, group in enumerate(match.groups()):
                    if group and i < len(entity_types):
                        entity = Entity(
                            type=entity_types[i],
                            value=group.strip(),
                            confidence=0.9
                        )
                        entities.append(entity)
                break
        
        return entities, confidence


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = IntentParser()
    
    test_commands = [
        "open chrome",
        "search for python tutorials",
        "what's the weather",
        "set timer for 5 minutes",
        "play some music",
        "what time is it",
        "volume up",
        "take a screenshot",
    ]
    
    print("Testing Intent Parser:\n")
    for command in test_commands:
        intent = parser.parse(command)
        print(f"Command: '{command}'")
        print(f"  Intent: {intent.type.value}")
        print(f"  Confidence: {intent.confidence:.2f}")
        if intent.entities:
            print(f"  Entities:")
            for entity in intent.entities:
                print(f"    - {entity.type}: '{entity.value}'")
        print()
