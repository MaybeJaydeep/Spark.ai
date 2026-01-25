#!/usr/bin/env python3
"""
Analytics Module for AI Assistant

Tracks usage statistics and performance metrics.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter


class AnalyticsTracker:
    """
    Analytics tracker for monitoring assistant usage and performance
    """
    
    def __init__(self, analytics_dir: str = "analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        
        self.session_start = time.time()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # In-memory counters
        self.counters = defaultdict(int)
        self.timers = {}
        self.events = []
        self.performance_metrics = defaultdict(list)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Auto-save timer
        self.auto_save_interval = 300  # 5 minutes
        self.last_save = time.time()
    
    def track_event(self, event_type: str, data: Dict[str, Any] = None):
        """
        Track an event
        
        Args:
            event_type: Type of event (e.g., 'command_executed', 'wake_word_detected')
            data: Additional event data
        """
        with self.lock:
            event = {
                "timestamp": time.time(),
                "session_id": self.session_id,
                "event_type": event_type,
                "data": data or {}
            }
            self.events.append(event)
            self.counters[event_type] += 1
            
            # Auto-save if needed
            if time.time() - self.last_save > self.auto_save_interval:
                self._save_session_data()
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """
        Increment a counter
        
        Args:
            counter_name: Name of the counter
            value: Value to increment by
        """
        with self.lock:
            self.counters[counter_name] += value
    
    def start_timer(self, timer_name: str):
        """
        Start a performance timer
        
        Args:
            timer_name: Name of the timer
        """
        with self.lock:
            self.timers[timer_name] = time.time()
    
    def stop_timer(self, timer_name: str) -> Optional[float]:
        """
        Stop a performance timer and record the duration
        
        Args:
            timer_name: Name of the timer
            
        Returns:
            Duration in seconds, or None if timer wasn't started
        """
        with self.lock:
            if timer_name in self.timers:
                duration = time.time() - self.timers[timer_name]
                del self.timers[timer_name]
                self.performance_metrics[timer_name].append(duration)
                return duration
            return None
    
    def record_performance_metric(self, metric_name: str, value: float):
        """
        Record a performance metric
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        with self.lock:
            self.performance_metrics[metric_name].append(value)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get current session statistics
        
        Returns:
            Dictionary of session statistics
        """
        with self.lock:
            session_duration = time.time() - self.session_start
            
            # Calculate performance averages
            perf_averages = {}
            for metric, values in self.performance_metrics.items():
                if values:
                    perf_averages[metric] = {
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
            
            return {
                "session_id": self.session_id,
                "session_duration": session_duration,
                "session_duration_formatted": self._format_duration(session_duration),
                "total_events": len(self.events),
                "event_counts": dict(self.counters),
                "performance_metrics": perf_averages,
                "active_timers": list(self.timers.keys()),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_command_statistics(self) -> Dict[str, Any]:
        """
        Get command usage statistics
        
        Returns:
            Dictionary of command statistics
        """
        with self.lock:
            command_events = [e for e in self.events if e["event_type"] == "command_executed"]
            
            if not command_events:
                return {"total_commands": 0, "command_types": {}, "success_rate": 0.0}
            
            # Count command types
            command_types = Counter()
            successful_commands = 0
            
            for event in command_events:
                data = event.get("data", {})
                intent_type = data.get("intent_type", "unknown")
                command_types[intent_type] += 1
                
                if data.get("success", False):
                    successful_commands += 1
            
            success_rate = successful_commands / len(command_events) * 100
            
            return {
                "total_commands": len(command_events),
                "command_types": dict(command_types),
                "success_rate": success_rate,
                "successful_commands": successful_commands,
                "failed_commands": len(command_events) - successful_commands
            }
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """
        Analyze usage patterns
        
        Returns:
            Dictionary of usage patterns
        """
        with self.lock:
            if not self.events:
                return {"hourly_usage": {}, "daily_usage": {}, "peak_hours": []}
            
            # Analyze by hour
            hourly_usage = defaultdict(int)
            daily_usage = defaultdict(int)
            
            for event in self.events:
                dt = datetime.fromtimestamp(event["timestamp"])
                hour = dt.hour
                day = dt.strftime("%Y-%m-%d")
                
                hourly_usage[hour] += 1
                daily_usage[day] += 1
            
            # Find peak hours
            peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "hourly_usage": dict(hourly_usage),
                "daily_usage": dict(daily_usage),
                "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
                "most_active_day": max(daily_usage.items(), key=lambda x: x[1]) if daily_usage else None
            }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"
    
    def _save_session_data(self):
        """Save current session data to file"""
        try:
            session_file = self.analytics_dir / f"session_{self.session_id}.json"
            stats = self.get_session_stats()
            
            with open(session_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            self.last_save = time.time()
            
        except Exception as e:
            print(f"Failed to save analytics data: {e}")
    
    def save_and_close(self):
        """Save final session data and close"""
        self._save_session_data()
        
        # Save command statistics
        try:
            cmd_stats_file = self.analytics_dir / f"commands_{self.session_id}.json"
            cmd_stats = self.get_command_statistics()
            
            with open(cmd_stats_file, 'w') as f:
                json.dump(cmd_stats, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save command statistics: {e}")
    
    def load_historical_data(self, days: int = 7) -> Dict[str, Any]:
        """
        Load historical analytics data
        
        Args:
            days: Number of days to load
            
        Returns:
            Historical analytics data
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        historical_data = {
            "sessions": [],
            "total_commands": 0,
            "total_session_time": 0,
            "command_types": Counter()
        }
        
        try:
            for session_file in self.analytics_dir.glob("session_*.json"):
                # Extract date from filename
                filename = session_file.stem
                date_str = filename.split("_")[1]  # session_YYYYMMDD_HHMMSS
                
                try:
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    if file_date >= cutoff_date:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                            historical_data["sessions"].append(session_data)
                            historical_data["total_session_time"] += session_data.get("session_duration", 0)
                            
                            # Load command data if available
                            cmd_file = self.analytics_dir / f"commands_{filename.split('_', 1)[1]}.json"
                            if cmd_file.exists():
                                with open(cmd_file, 'r') as cf:
                                    cmd_data = json.load(cf)
                                    historical_data["total_commands"] += cmd_data.get("total_commands", 0)
                                    for cmd_type, count in cmd_data.get("command_types", {}).items():
                                        historical_data["command_types"][cmd_type] += count
                                        
                except ValueError:
                    continue  # Skip files with invalid date format
                    
        except Exception as e:
            print(f"Failed to load historical data: {e}")
        
        return historical_data


# Global analytics instance
_analytics_instance: Optional[AnalyticsTracker] = None


def get_analytics() -> AnalyticsTracker:
    """Get the global analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsTracker()
    return _analytics_instance


# Convenience functions
def track_command_execution(intent_type: str, success: bool, duration: float = None):
    """Track command execution"""
    analytics = get_analytics()
    analytics.track_event("command_executed", {
        "intent_type": intent_type,
        "success": success,
        "duration": duration
    })


def track_wake_word_detection(wake_word: str, confidence: float = None):
    """Track wake word detection"""
    analytics = get_analytics()
    analytics.track_event("wake_word_detected", {
        "wake_word": wake_word,
        "confidence": confidence
    })


def track_voice_recognition(success: bool, duration: float = None, text: str = None):
    """Track voice recognition attempt"""
    analytics = get_analytics()
    analytics.track_event("voice_recognition", {
        "success": success,
        "duration": duration,
        "text_length": len(text) if text else 0
    })


if __name__ == "__main__":
    # Test analytics system
    print("📊 Testing Analytics System")
    print("=" * 40)
    
    analytics = AnalyticsTracker()
    
    # Simulate some events
    analytics.track_event("wake_word_detected", {"wake_word": "hey assistant"})
    analytics.track_event("command_executed", {"intent_type": "open_app", "success": True})
    analytics.track_event("command_executed", {"intent_type": "volume_up", "success": True})
    
    # Test performance timing
    analytics.start_timer("test_operation")
    time.sleep(0.1)
    duration = analytics.stop_timer("test_operation")
    print(f"Test operation took: {duration:.4f} seconds")
    
    # Get statistics
    stats = analytics.get_session_stats()
    print(f"\nSession Statistics:")
    print(f"  Events: {stats['total_events']}")
    print(f"  Duration: {stats['session_duration_formatted']}")
    
    cmd_stats = analytics.get_command_statistics()
    print(f"\nCommand Statistics:")
    print(f"  Total commands: {cmd_stats['total_commands']}")
    print(f"  Success rate: {cmd_stats['success_rate']:.1f}%")
    
    print("\n✅ Analytics system working!")