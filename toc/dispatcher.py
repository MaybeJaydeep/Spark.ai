"""
Task Orchestration and Command Dispatcher

Coordinates between intent parsing and action execution.
"""

import logging
from typing import Optional
from nlp.intent_parser import Intent, IntentType
from actions.apps import AppController
from actions.system import SystemController
from actions.timer import get_timer_manager
import math
import os
import requests


class CommandDispatcher:
    """
    Command Dispatcher
    
    Orchestrates the execution of commands by routing intents
    to the appropriate action controllers.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app_controller = AppController()
        self.system_controller = SystemController()
        self.timer_manager = get_timer_manager()
    
    def dispatch(self, intent: Intent) -> dict:
        """
        Dispatch an intent to the appropriate action handler
        
        Args:
            intent: Parsed intent to execute
            
        Returns:
            Dictionary with execution result
        """
        self.logger.info(f"Dispatching intent: {intent.type.value}")
        
        try:
            if intent.type == IntentType.OPEN_APP:
                return self._handle_open_app(intent)
            
            elif intent.type == IntentType.CLOSE_APP:
                return self._handle_close_app(intent)
            
            elif intent.type == IntentType.SEARCH:
                return self._handle_search(intent)
            
            elif intent.type == IntentType.PLAY_MUSIC:
                return self._handle_play_music(intent)
            
            elif intent.type == IntentType.SET_TIMER:
                return self._handle_set_timer(intent)
            
            elif intent.type == IntentType.GET_WEATHER:
                return self._handle_get_weather(intent)
            
            elif intent.type == IntentType.GET_TIME:
                return self._handle_get_time(intent)

            elif intent.type == IntentType.CALCULATE:
                return self._handle_calculate(intent)
            
            elif intent.type == IntentType.VOLUME_UP:
                return self._handle_volume_up(intent)
            
            elif intent.type == IntentType.VOLUME_DOWN:
                return self._handle_volume_down(intent)
            
            elif intent.type == IntentType.MUTE:
                return self._handle_mute(intent)
            
            elif intent.type == IntentType.UNMUTE:
                return self._handle_unmute(intent)
            
            elif intent.type == IntentType.LOCK_SCREEN:
                return self._handle_lock_screen(intent)
            
            elif intent.type == IntentType.TAKE_SCREENSHOT:
                return self._handle_screenshot(intent)
            
            elif intent.type == IntentType.PLAY_MEDIA:
                return self._handle_play_media(intent)
            
            elif intent.type == IntentType.PAUSE_MEDIA:
                return self._handle_pause_media(intent)
            
            elif intent.type == IntentType.NEXT_TRACK:
                return self._handle_next_track(intent)
            
            elif intent.type == IntentType.PREVIOUS_TRACK:
                return self._handle_previous_track(intent)
            
            elif intent.type == IntentType.SHUTDOWN:
                return self._handle_shutdown(intent)
            
            elif intent.type == IntentType.UNKNOWN:
                return {
                    "success": False,
                    "message": "I didn't understand that command",
                    "intent": intent.type.value
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Action for '{intent.type.value}' not yet implemented",
                    "intent": intent.type.value
                }
                
        except Exception as e:
            self.logger.error(f"Error dispatching intent: {e}")
            return {
                "success": False,
                "message": f"Error executing command: {str(e)}",
                "intent": intent.type.value
            }
    
    def _handle_open_app(self, intent: Intent) -> dict:
        """Handle open app intent"""
        app_entity = intent.get_entity("app_name")
        if not app_entity:
            return {
                "success": False,
                "message": "No app name specified",
                "intent": intent.type.value
            }
        
        app_name = app_entity.value
        success = self.app_controller.open_app(app_name)
        
        return {
            "success": success,
            "message": f"Opened {app_name}" if success else f"Failed to open {app_name}",
            "intent": intent.type.value,
            "app_name": app_name
        }
    
    def _handle_close_app(self, intent: Intent) -> dict:
        """Handle close app intent"""
        app_entity = intent.get_entity("app_name")
        if not app_entity:
            return {
                "success": False,
                "message": "No app name specified",
                "intent": intent.type.value
            }
        
        app_name = app_entity.value
        success = self.app_controller.close_app(app_name)
        
        return {
            "success": success,
            "message": f"Closed {app_name}" if success else f"Failed to close {app_name}",
            "intent": intent.type.value,
            "app_name": app_name
        }
    
    def _handle_search(self, intent: Intent) -> dict:
        """Handle search intent"""
        query_entity = intent.get_entity("query")
        if not query_entity:
            return {
                "success": False,
                "message": "No search query specified",
                "intent": intent.type.value
            }
        
        query = query_entity.value
        success = self.app_controller.search_web(query)
        
        return {
            "success": success,
            "message": f"Searched for: {query}" if success else "Failed to open search",
            "intent": intent.type.value,
            "query": query
        }
    
    def _handle_play_music(self, intent: Intent) -> dict:
        """Handle play music intent"""
        song_entity = intent.get_entity("song_name")
        
        if song_entity:
            song = song_entity.value
            # Try to open Spotify or music player
            success = self.app_controller.open_app("spotify")
            message = f"Opening Spotify to play {song}" if success else "Failed to open music player"
        else:
            success = self.app_controller.open_app("spotify")
            message = "Opening Spotify" if success else "Failed to open music player"
        
        return {
            "success": success,
            "message": message,
            "intent": intent.type.value
        }
    
    def _handle_set_timer(self, intent: Intent) -> dict:
        """Handle set timer intent"""
        duration_entity = intent.get_entity("duration")
        unit_entity = intent.get_entity("unit")
        
        if not duration_entity or not unit_entity:
            return {
                "success": False,
                "message": "Timer duration not specified",
                "intent": intent.type.value
            }
        
        try:
            duration = int(duration_entity.value)
            unit = unit_entity.value.lower()
            
            # Convert to seconds
            if "minute" in unit:
                duration_seconds = duration * 60
                unit_display = "minute" if duration == 1 else "minutes"
            elif "second" in unit:
                duration_seconds = duration
                unit_display = "second" if duration == 1 else "seconds"
            elif "hour" in unit:
                duration_seconds = duration * 3600
                unit_display = "hour" if duration == 1 else "hours"
            else:
                return {
                    "success": False,
                    "message": f"Unknown time unit: {unit}",
                    "intent": intent.type.value
                }
            
            # Create timer with notification callback
            def on_timer_finished(timer):
                self.logger.info(f"⏰ Timer '{timer.name}' finished!")
                # Could add system notification here
            
            timer_name = f"Timer_{duration}_{unit_display}"
            timer = self.timer_manager.create_timer(
                duration_seconds,
                name=timer_name,
                callback=on_timer_finished
            )
            
            return {
                "success": True,
                "message": f"Timer set for {duration} {unit_display}",
                "intent": intent.type.value,
                "duration": duration,
                "unit": unit_display,
                "timer_name": timer_name
            }
            
        except ValueError:
            return {
                "success": False,
                "message": "Invalid timer duration",
                "intent": intent.type.value
            }
        except Exception as e:
            self.logger.error(f"Error setting timer: {e}")
            return {
                "success": False,
                "message": f"Failed to set timer: {str(e)}",
                "intent": intent.type.value
            }
    
    def _handle_get_weather(self, intent: Intent) -> dict:
        """Handle get weather intent using OpenWeatherMap API if configured"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        location_entity = intent.get_entity("location")
        city = location_entity.value if location_entity else "London"

        if not api_key:
            # Fallback to browser-based search
            query = f"weather in {city}"
            success = self.app_controller.search_web(query)
            return {
                "success": success,
                "message": f"Opening weather search for {city}" if success else "Failed to get weather",
                "intent": intent.type.value,
            }

        try:
            params = {"q": city, "appid": api_key, "units": "metric"}
            resp = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            main = data.get("weather", [{}])[0].get("description", "").capitalize()
            temp = data.get("main", {}).get("temp")
            feels = data.get("main", {}).get("feels_like")

            if temp is None:
                raise ValueError("No temperature data")

            msg = f"The weather in {city} is {main}, {temp:.1f}°C (feels like {feels:.1f}°C)."
            return {
                "success": True,
                "message": msg,
                "intent": intent.type.value,
                "city": city,
            }
        except Exception as e:
            self.logger.error(f"Weather API error: {e}")
            return {
                "success": False,
                "message": f"Sorry, I couldn't fetch the weather for {city}",
                "intent": intent.type.value,
            }
    
    def _handle_get_time(self, intent: Intent) -> dict:
        """Handle get time intent"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        
        return {
            "success": True,
            "message": f"The time is {current_time}",
            "intent": intent.type.value,
            "time": current_time
        }

    def _handle_calculate(self, intent: Intent) -> dict:
        """Handle quick math / calculation intent"""
        expr_entity = intent.get_entity("expression")
        if not expr_entity:
            return {
                "success": False,
                "message": "No expression to calculate",
                "intent": intent.type.value,
            }

        expression = expr_entity.value
        
        # Validate expression for security
        from validators import validate_math_expression
        is_valid, error_msg = validate_math_expression(expression)
        if not is_valid:
            return {
                "success": False,
                "message": f"Invalid expression: {error_msg}",
                "intent": intent.type.value,
            }

        # Very small, safe eval environment
        allowed_names = {
            k: getattr(math, k)
            for k in ["sqrt", "sin", "cos", "tan", "log", "log10", "pi", "e", "ceil", "floor"]
        }
        allowed_names["abs"] = abs
        allowed_names["round"] = round
        allowed_names["min"] = min
        allowed_names["max"] = max

        try:
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # Format result nicely
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)  # Limit decimal places
            
            return {
                "success": True,
                "message": f"{expression} = {result}",
                "intent": intent.type.value,
                "expression": expression,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Sorry, I couldn't calculate '{expression}': {str(e)}",
                "intent": intent.type.value,
            }
    
    def _handle_volume_up(self, intent: Intent) -> dict:
        """Handle volume up intent"""
        success = self.system_controller.volume_up(10)
        
        return {
            "success": success,
            "message": "Volume increased" if success else "Failed to increase volume",
            "intent": intent.type.value
        }
    
    def _handle_volume_down(self, intent: Intent) -> dict:
        """Handle volume down intent"""
        success = self.system_controller.volume_down(10)
        
        return {
            "success": success,
            "message": "Volume decreased" if success else "Failed to decrease volume",
            "intent": intent.type.value
        }
    
    def _handle_mute(self, intent: Intent) -> dict:
        """Handle mute intent"""
        success = self.system_controller.mute()
        
        return {
            "success": success,
            "message": "Audio muted" if success else "Failed to mute audio",
            "intent": intent.type.value
        }
    
    def _handle_unmute(self, intent: Intent) -> dict:
        """Handle unmute intent"""
        success = self.system_controller.unmute()
        
        return {
            "success": success,
            "message": "Audio unmuted" if success else "Failed to unmute audio",
            "intent": intent.type.value
        }
    
    def _handle_lock_screen(self, intent: Intent) -> dict:
        """Handle lock screen intent"""
        success = self.system_controller.lock_screen()
        
        return {
            "success": success,
            "message": "Screen locked" if success else "Failed to lock screen",
            "intent": intent.type.value
        }
    
    def _handle_screenshot(self, intent: Intent) -> dict:
        """Handle screenshot intent"""
        success, filepath = self.system_controller.take_screenshot()
        
        return {
            "success": success,
            "message": f"Screenshot saved to {filepath}" if success else "Failed to take screenshot",
            "intent": intent.type.value,
            "filepath": filepath if success else None
        }
    
    def _handle_play_media(self, intent: Intent) -> dict:
        """Handle play media intent"""
        success = self.system_controller.play_media()
        return {
            "success": success,
            "message": "Media playing" if success else "Failed to play media",
            "intent": intent.type.value
        }
    
    def _handle_pause_media(self, intent: Intent) -> dict:
        """Handle pause media intent"""
        success = self.system_controller.pause_media()
        return {
            "success": success,
            "message": "Media paused" if success else "Failed to pause media",
            "intent": intent.type.value
        }
    
    def _handle_next_track(self, intent: Intent) -> dict:
        """Handle next track intent"""
        success = self.system_controller.next_track()
        return {
            "success": success,
            "message": "Skipped to next track" if success else "Failed to skip track",
            "intent": intent.type.value
        }
    
    def _handle_previous_track(self, intent: Intent) -> dict:
        """Handle previous track intent"""
        success = self.system_controller.previous_track()
        return {
            "success": success,
            "message": "Went to previous track" if success else "Failed to go to previous track",
            "intent": intent.type.value
        }
    
    def _handle_shutdown(self, intent: Intent) -> dict:
        """Handle shutdown intent"""
        # Don't actually shutdown without explicit confirmation
        return {
            "success": False,
            "message": "Shutdown requires explicit confirmation for safety",
            "intent": intent.type.value
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from nlp.intent_parser import IntentParser
    
    dispatcher = CommandDispatcher()
    parser = IntentParser()
    
    # Test commands
    test_commands = [
        "open firefox",
        "search for python",
        "what time is it",
        "volume up",
        "take a screenshot"
    ]
    
    print("Testing CommandDispatcher:\n")
    for command in test_commands:
        print(f"Command: '{command}'")
        intent = parser.parse(command)
        result = dispatcher.dispatch(intent)
        print(f"  Result: {result['message']}")
        print(f"  Success: {result['success']}")
        print()