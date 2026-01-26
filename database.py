#!/usr/bin/env python3
"""
Database Module for AI Assistant

Provides simple database operations for storing assistant data.
"""

import sqlite3
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime


class AssistantDatabase:
    """
    Simple SQLite database for storing assistant data
    """
    
    def __init__(self, db_path: str = "data/assistant.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    session_id TEXT NOT NULL,
                    command_text TEXT NOT NULL,
                    intent_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    execution_time REAL,
                    error_message TEXT,
                    entities TEXT  -- JSON string
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    total_commands INTEGER DEFAULT 0,
                    successful_commands INTEGER DEFAULT 0,
                    mode TEXT NOT NULL,
                    wake_word_activations INTEGER DEFAULT 0
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            ''')
            
            # Error logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT  -- JSON string
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def log_command(self, session_id: str, command_text: str, intent_type: str, 
                   confidence: float, success: bool, execution_time: float = None,
                   error_message: str = None, entities: List[Dict] = None):
        """
        Log a command execution
        
        Args:
            session_id: Session identifier
            command_text: Original command text
            intent_type: Parsed intent type
            confidence: Intent confidence score
            success: Whether command succeeded
            execution_time: Time taken to execute
            error_message: Error message if failed
            entities: Extracted entities
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            entities_json = json.dumps(entities) if entities else None
            
            cursor.execute('''
                INSERT INTO commands 
                (timestamp, session_id, command_text, intent_type, confidence, 
                 success, execution_time, error_message, entities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(), session_id, command_text, intent_type, confidence,
                success, execution_time, error_message, entities_json
            ))
            
            conn.commit()
    
    def start_session(self, session_id: str, mode: str):
        """
        Start a new session
        
        Args:
            session_id: Session identifier
            mode: Session mode (interactive, handsfree, etc.)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, start_time, mode)
                VALUES (?, ?, ?)
            ''', (session_id, time.time(), mode))
            
            conn.commit()
    
    def end_session(self, session_id: str, total_commands: int = 0, 
                   successful_commands: int = 0, wake_word_activations: int = 0):
        """
        End a session
        
        Args:
            session_id: Session identifier
            total_commands: Total commands in session
            successful_commands: Successful commands in session
            wake_word_activations: Wake word activations in session
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET end_time = ?, total_commands = ?, successful_commands = ?, 
                    wake_word_activations = ?
                WHERE session_id = ?
            ''', (time.time(), total_commands, successful_commands, 
                  wake_word_activations, session_id))
            
            conn.commit()
    
    def set_user_preference(self, key: str, value: Any):
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            value_json = json.dumps(value)
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences 
                (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value_json, time.time()))
            
            conn.commit()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM user_preferences WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['value'])
            return default
    
    def log_performance_metric(self, metric_name: str, metric_value: float, 
                              metric_unit: str = "count", category: str = "general"):
        """
        Log a performance metric
        
        Args:
            metric_name: Name of the metric
            metric_value: Metric value
            metric_unit: Unit of measurement
            category: Metric category
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_name, metric_value, metric_unit, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), metric_name, metric_value, metric_unit, category))
            
            conn.commit()
    
    def log_error(self, error_type: str, error_message: str, 
                  stack_trace: str = None, context: Dict = None):
        """
        Log an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace if available
            context: Additional context information
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            context_json = json.dumps(context) if context else None
            
            cursor.execute('''
                INSERT INTO error_logs 
                (timestamp, error_type, error_message, stack_trace, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), error_type, error_message, stack_trace, context_json))
            
            conn.commit()
    
    def get_command_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get command statistics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Command statistics
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total commands
            cursor.execute('''
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM commands 
                WHERE timestamp >= ?
            ''', (cutoff_time,))
            
            totals = cursor.fetchone()
            
            # Command types
            cursor.execute('''
                SELECT intent_type, COUNT(*) as count,
                       AVG(confidence) as avg_confidence,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                FROM commands 
                WHERE timestamp >= ?
                GROUP BY intent_type
                ORDER BY count DESC
            ''', (cutoff_time,))
            
            command_types = cursor.fetchall()
            
            # Average execution time
            cursor.execute('''
                SELECT AVG(execution_time) as avg_execution_time
                FROM commands 
                WHERE timestamp >= ? AND execution_time IS NOT NULL
            ''', (cutoff_time,))
            
            avg_time = cursor.fetchone()
            
            return {
                'total_commands': totals['total'],
                'successful_commands': totals['successful'],
                'success_rate': (totals['successful'] / totals['total'] * 100) if totals['total'] > 0 else 0,
                'average_execution_time': avg_time['avg_execution_time'] or 0,
                'command_types': [dict(row) for row in command_types],
                'days_analyzed': days
            }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent session history
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions 
                ORDER BY start_time DESC 
                LIMIT ?
            ''', (limit,))
            
            sessions = cursor.fetchall()
            return [dict(row) for row in sessions]
    
    def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get error summary for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Error summary
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT error_type, COUNT(*) as count
                FROM error_logs 
                WHERE timestamp >= ?
                GROUP BY error_type
                ORDER BY count DESC
            ''', (cutoff_time,))
            
            error_types = cursor.fetchall()
            
            cursor.execute('''
                SELECT COUNT(*) as total_errors
                FROM error_logs 
                WHERE timestamp >= ?
            ''', (cutoff_time,))
            
            total = cursor.fetchone()
            
            return {
                'total_errors': total['total_errors'],
                'error_types': [dict(row) for row in error_types],
                'days_analyzed': days
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old data to keep database size manageable
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean up old commands
            cursor.execute('DELETE FROM commands WHERE timestamp < ?', (cutoff_time,))
            
            # Clean up old performance metrics
            cursor.execute('DELETE FROM performance_metrics WHERE timestamp < ?', (cutoff_time,))
            
            # Clean up old error logs
            cursor.execute('DELETE FROM error_logs WHERE timestamp < ?', (cutoff_time,))
            
            # Clean up old sessions
            cursor.execute('DELETE FROM sessions WHERE start_time < ?', (cutoff_time,))
            
            conn.commit()
            
            # Vacuum database to reclaim space
            cursor.execute('VACUUM')


# Global database instance
_database_instance: Optional[AssistantDatabase] = None


def get_database() -> AssistantDatabase:
    """Get the global database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = AssistantDatabase()
    return _database_instance


if __name__ == "__main__":
    # Test database functionality
    print("🗄️  Testing Database System")
    print("=" * 40)
    
    db = AssistantDatabase("test_assistant.db")
    
    # Test session
    session_id = f"test_{int(time.time())}"
    print(f"\n📝 Starting test session: {session_id}")
    
    db.start_session(session_id, "test")
    
    # Test command logging
    db.log_command(
        session_id=session_id,
        command_text="test command",
        intent_type="test_intent",
        confidence=0.95,
        success=True,
        execution_time=0.1,
        entities=[{"type": "test", "value": "example"}]
    )
    
    # Test preferences
    db.set_user_preference("test_pref", {"value": 42, "enabled": True})
    pref = db.get_user_preference("test_pref")
    print(f"Preference: {pref}")
    
    # Test performance metric
    db.log_performance_metric("test_metric", 1.23, "seconds", "test")
    
    # End session
    db.end_session(session_id, 1, 1, 0)
    
    # Get statistics
    stats = db.get_command_statistics(1)
    print(f"\nCommand Statistics: {stats}")
    
    # Get session history
    history = db.get_session_history(5)
    print(f"Session History: {len(history)} sessions")
    
    print("\n✅ Database system working!")
    
    # Clean up test database
    Path("test_assistant.db").unlink(missing_ok=True)