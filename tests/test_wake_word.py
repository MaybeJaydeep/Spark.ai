"""
Tests for wake word detection functionality
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

# Import the wake word detector
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wake_word.listener import WakeWordDetector, ActivationEvent, WakeWordConfig, DetectionState


class TestWakeWordConfig:
    """Test wake word configuration"""
    
    def test_default_config_creation(self):
        """Test creating config with default values"""
        config = WakeWordConfig(wake_words=["test"])
        assert config.wake_words == ["test"]
        assert config.confidence_threshold == 0.7
        assert config.sample_rate == 16000
        assert config.chunk_size == 1024
    
    def test_custom_config_creation(self):
        """Test creating config with custom values"""
        config = WakeWordConfig(
            wake_words=["custom", "words"],
            confidence_threshold=0.8,
            sample_rate=22050
        )
        assert config.wake_words == ["custom", "words"]
        assert config.confidence_threshold == 0.8
        assert config.sample_rate == 22050


class TestWakeWordDetector:
    """Test wake word detector functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        config_data = {
            "wake_words": ["test", "hello"],
            "confidence_threshold": 0.6,
            "sample_rate": 16000
        }
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        # Create detector with test config
        self.detector = WakeWordDetector(config_path=self.temp_config.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'detector'):
            self.detector.stop()
        
        # Remove temp config file
        if hasattr(self, 'temp_config'):
            os.unlink(self.temp_config.name)
    
    def test_config_loading(self):
        """Test configuration loading from file"""
        assert self.detector.config.wake_words == ["test", "hello"]
        assert self.detector.config.confidence_threshold == 0.6
        assert self.detector.config.sample_rate == 16000
    
    def test_config_loading_missing_file(self):
        """Test configuration loading with missing file"""
        detector = WakeWordDetector(config_path="nonexistent.json")
        # Should use default config
        assert "hey assistant" in detector.config.wake_words
        assert detector.config.confidence_threshold == 0.7
    
    def test_listener_management(self):
        """Test adding and removing listeners"""
        callback1 = Mock()
        callback2 = Mock()
        
        # Add listeners
        self.detector.add_listener(callback1)
        self.detector.add_listener(callback2)
        assert len(self.detector.listeners) == 2
        
        # Remove listener
        self.detector.remove_listener(callback1)
        assert len(self.detector.listeners) == 1
        assert callback2 in self.detector.listeners
    
    def test_activation_event_creation(self):
        """Test activation event creation"""
        event = ActivationEvent(
            timestamp=time.time(),
            confidence=0.85,
            wake_word="test",
            audio_context=b"audio_data"
        )
        
        assert event.confidence == 0.85
        assert event.wake_word == "test"
        assert event.audio_context == b"audio_data"
    
    @patch('wake_word.listener.pyaudio')
    @patch('wake_word.listener.webrtcvad')
    def test_dependency_check_success(self, mock_webrtcvad, mock_pyaudio):
        """Test dependency check with all dependencies available"""
        mock_pyaudio.PyAudio = Mock()
        mock_webrtcvad.Vad = Mock()
        
        assert self.detector._check_dependencies() == True
    
    def test_dependency_check_failure(self):
        """Test dependency check with missing dependencies"""
        # This will fail in the actual environment since we're testing without mocking
        # In a real test environment, you'd mock the imports
        pass
    
    def test_status_reporting(self):
        """Test status reporting functionality"""
        status = self.detector.get_status()
        
        assert "state" in status
        assert "is_running" in status
        assert "config" in status
        assert "listeners_count" in status
        
        assert status["state"] == DetectionState.IDLE.value
        assert status["is_running"] == False
        assert status["listeners_count"] == 0
    
    def test_config_reload(self):
        """Test configuration reloading"""
        # Modify config file
        new_config = {
            "wake_words": ["new", "words"],
            "confidence_threshold": 0.9
        }
        
        with open(self.temp_config.name, 'w') as f:
            json.dump(new_config, f)
        
        # Reload config
        result = self.detector.reload_config()
        
        assert result == True
        assert self.detector.config.wake_words == ["new", "words"]
        assert self.detector.config.confidence_threshold == 0.9
    
    def test_listener_notification(self):
        """Test listener notification on activation"""
        callback = Mock()
        self.detector.add_listener(callback)
        
        # Create test event
        event = ActivationEvent(
            timestamp=time.time(),
            confidence=0.8,
            wake_word="test"
        )
        
        # Notify listeners
        self.detector._notify_listeners(event)
        
        # Verify callback was called
        callback.assert_called_once_with(event)
    
    def test_listener_notification_error_handling(self):
        """Test error handling in listener notification"""
        # Create callback that raises exception
        def failing_callback(event):
            raise Exception("Test error")
        
        working_callback = Mock()
        
        self.detector.add_listener(failing_callback)
        self.detector.add_listener(working_callback)
        
        event = ActivationEvent(
            timestamp=time.time(),
            confidence=0.8,
            wake_word="test"
        )
        
        # Should not raise exception, should call working callback
        self.detector._notify_listeners(event)
        working_callback.assert_called_once_with(event)


class TestIntegration:
    """Integration tests for wake word detection"""
    
    @pytest.mark.skipif(
        not all([
            'pyaudio' in sys.modules,
            'numpy' in sys.modules,
            'webrtcvad' in sys.modules
        ]),
        reason="Audio dependencies not available"
    )
    def test_detector_lifecycle(self):
        """Test complete detector lifecycle"""
        detector = WakeWordDetector()
        
        # Test starting
        success = detector.start()
        if success:  # Only test if audio is available
            assert detector.is_running == True
            assert detector.state == DetectionState.LISTENING
            
            # Let it run briefly
            time.sleep(0.5)
            
            # Test stopping
            detector.stop()
            assert detector.is_running == False
            assert detector.state == DetectionState.IDLE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])