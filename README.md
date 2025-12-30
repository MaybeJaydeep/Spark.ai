# AI Assistant - Wake Word Detection

A Python-based AI assistant with continuous wake word detection capabilities. This project implements real-time audio monitoring to detect configurable wake words and activate the assistant hands-free.

## 🚀 Features

- **Continuous Audio Monitoring** - Real-time listening without blocking other operations
- **Configurable Wake Words** - Support for multiple custom wake words
- **Voice Activity Detection** - Intelligent filtering using WebRTC VAD
- **Event-Driven Architecture** - Modular design for easy integration
- **Low Resource Usage** - Optimized for continuous operation
- **Cross-Platform** - Works on Windows, macOS, and Linux

## 📋 Requirements

- Python 3.8 or higher
- Microphone access
- Audio drivers (PortAudio)

## 🛠️ Installation

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-assistant
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Start the assistant**
   ```bash
   python main.py
   ```

### Manual Installation

1. **Install system dependencies**

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install portaudio19-dev python3-pyaudio alsa-utils
   ```

   **macOS:**
   ```bash
   brew install portaudio
   ```

   **Windows:**
   No additional system dependencies needed.

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎤 Usage

### Basic Usage

```bash
python main.py
```

The assistant will start listening for wake words. Default wake words include:
- "hey assistant"
- "computer" 
- "wake up"
- "hello assistant"

### Configuration

Edit `config/wake_word_config.json` to customize settings:

```json
{
  "wake_words": [
    "hey assistant",
    "computer",
    "wake up"
  ],
  "confidence_threshold": 0.7,
  "sample_rate": 16000,
  "chunk_size": 1024,
  "channels": 1,
  "buffer_duration": 2.0,
  "vad_aggressiveness": 2
}
```

### Programmatic Usage

```python
from wake_word.listener import WakeWordDetector, ActivationEvent

def on_wake_word(event: ActivationEvent):
    print(f"Wake word detected: {event.wake_word}")
    print(f"Confidence: {event.confidence}")

# Create and start detector
detector = WakeWordDetector()
detector.add_listener(on_wake_word)
detector.start()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    detector.stop()
```

## 🏗️ Architecture

### Core Components

- **`WakeWordDetector`** - Main detection engine
- **`ActivationEvent`** - Event data structure for wake word detections
- **`WakeWordConfig`** - Configuration management
- **`DetectionState`** - State tracking enum

### Audio Processing Pipeline

1. **Audio Capture** - Continuous microphone monitoring
2. **Voice Activity Detection** - Filter out silence and noise
3. **Wake Word Detection** - Pattern matching against configured words
4. **Event Generation** - Create activation events for detected words
5. **Listener Notification** - Notify registered callbacks

### State Management

- `IDLE` - Detector not running
- `LISTENING` - Actively monitoring audio
- `PROCESSING` - Analyzing audio for wake words
- `DETECTED` - Wake word found, event generated
- `ERROR` - Error state with automatic recovery

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run specific tests:

```bash
python -m pytest tests/test_wake_word.py -v
```

### Test Coverage

- Configuration loading and validation
- Listener management (add/remove callbacks)
- Event generation and notification
- Error handling and recovery
- Audio processing pipeline
- Integration tests (when audio hardware available)

## 🔧 Configuration Options

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `wake_words` | List of trigger phrases | `["hey assistant", ...]` | Any strings |
| `confidence_threshold` | Minimum confidence for detection | `0.7` | 0.0 - 1.0 |
| `sample_rate` | Audio sample rate (Hz) | `16000` | 8000 - 48000 |
| `chunk_size` | Audio buffer size | `1024` | 256 - 4096 |
| `channels` | Audio channels | `1` | 1 - 2 |
| `buffer_duration` | Audio buffer duration (seconds) | `2.0` | 0.5 - 10.0 |
| `vad_aggressiveness` | Voice activity detection sensitivity | `2` | 0 - 3 |

## 🚨 Troubleshooting

### Common Issues

**"No audio input devices found"**
- Check microphone permissions
- Verify microphone is connected and working
- Try running: `python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_device_count())"`

**"ImportError: No module named 'pyaudio'"**
- Install system audio dependencies first
- On Linux: `sudo apt-get install portaudio19-dev`
- On macOS: `brew install portaudio`
- Then: `pip install pyaudio`

**High CPU usage**
- Reduce `sample_rate` in config
- Increase `chunk_size` in config
- Adjust `vad_aggressiveness` to filter more audio

**False positive detections**
- Increase `confidence_threshold`
- Adjust `vad_aggressiveness`
- Review and refine wake word list

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

- **Advanced Wake Word Models** - Integration with Porcupine or custom neural networks
- **Noise Cancellation** - Advanced audio preprocessing
- **Multiple Language Support** - Wake words in different languages
- **Cloud Integration** - Remote wake word model updates
- **Performance Metrics** - Detection accuracy and latency monitoring

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information

---

**Note:** This is currently a demonstration implementation. The wake word detection uses a simple energy-based approach. For production use, consider integrating with specialized wake word detection libraries like Porcupine or training custom models.