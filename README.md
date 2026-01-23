# AI Assistant - Voice-Controlled AI Assistant

A complete Python-based AI voice assistant with speech recognition, natural language understanding, and system control capabilities.

## 🎉 Features

### ✅ Fully Working
- **Voice Recognition** - Speak commands naturally
- **Wake Word Detection** - Hands-free activation
- **Intent Parsing** - Understands 15+ command types
- **App Control** - Open/close applications
- **System Control** - Volume, screenshots, power management
- **Timer Functionality** - Set countdown timers
- **Text-to-Speech** - Voice responses (optional)
- **Web Search** - Search the internet
- **Time Queries** - Get current time
- **Text Mode** - Type commands (no mic needed)
- **GUI Interface** - Visual status and feedback

### 🎤 Voice Commands
- "open firefox" / "open vlc" - Launch applications
- "close chrome" - Close applications
- "search for python tutorials" - Web search
- "what time is it" - Get current time
- "volume up" / "volume down" - Control volume
- "mute" / "unmute" - Audio control
- "take a screenshot" - Capture screen
- "set timer for 5 minutes" - Set countdown timer
- "lock screen" - Lock your computer
- **Media Controls (NEW!):**
  - "play video" / "resume" - Play/resume media in VLC or YouTube
  - "pause video" - Pause media
  - "next track" / "skip" - Skip to next track
  - "previous track" / "back" - Go to previous track
- **Quick Math (NEW!):**
  - "calculate 23 * 45" - Get instant calculations
  - "what is 10 / 3" - Math expressions
- **Weather (NEW!):**
  - "what's the weather" - Get weather (requires OPENWEATHER_API_KEY)
  - "what's the weather in New York" - Weather for specific location

## 🚀 Quick Start

### Easy Launcher (Recommended)
```bash
python run_assistant.py
```

This shows a menu with all available modes.

### Hands-Free Mode (NEW!)
```bash
python voice_assistant_handsfree.py
```
Say "hey assistant" or "computer" to activate. Add `--no-tts` to disable voice responses.

### Interactive Voice Mode
```bash
python voice_assistant.py
```
Press ENTER to speak. Add `--tts` to enable voice responses.

**Text Assistant (No Microphone):**
```bash
python test_assistant.py
```

**GUI Mode:**
```bash
python main.py --gui
```

**Modern GUI Mode (Recommended):**
```bash
python main.py --gui-modern
```

**Test Voice:**
```bash
python test_voice.py
```

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Additional Packages
```bash
pip install sounddevice soundfile SpeechRecognition numpy pywin32
```

### 4. Test Installation
```bash
python test_microphone.py
```

## 🎯 Usage Modes

### 1. Interactive Voice Mode
Press ENTER, speak your command, get results.
```bash
python voice_assistant.py --mode interactive
```

### 2. Continuous Voice Mode
Always listening (no button press needed).
```bash
python voice_assistant.py --mode continuous
```

### 3. Text Mode
Type commands instead of speaking.
```bash
python test_assistant.py
```

### 4. GUI Mode
Visual interface with status indicators.
```bash
python main.py --gui
```

### 5. Modern GUI Mode (Recommended)
Modern UI with text + voice controls.
```bash
python main.py --gui-modern
```

## 🏗️ Architecture

```
AI-assistant/
├── speech/
│   ├── stt.py                 # Speech-to-text (PyAudio)
│   ├── stt_sounddevice.py     # Speech-to-text (sounddevice) ✅
│   └── stt_windows.py         # Windows Speech API fallback
├── nlp/
│   └── intent_parser.py       # Natural language understanding
├── actions/
│   ├── apps.py                # Application control
│   └── system.py              # System operations
├── toc/
│   └── dispatcher.py          # Command routing
├── ui/
│   └── app.py                 # GUI interface
├── wake_word/
│   └── listener.py            # Wake word detection (needs PyAudio)
├── voice_assistant.py         # Complete voice assistant ✅
├── test_assistant.py          # Text-based testing ✅
├── test_voice.py              # Voice input testing ✅
├── run_assistant.py           # Easy launcher ✅
└── main.py                    # Main application
```

## 🔧 Configuration

### Wake Word Config
Edit `config/wake_word_config.json`:
```json
{
  "wake_words": ["hey assistant", "computer"],
  "confidence_threshold": 0.7,
  "sample_rate": 16000
}
```

## 🧪 Testing

### Test All Components
```bash
python test_microphone.py
```

### Test Voice Recognition
```bash
python test_voice.py
```

### Test Intent Parser
```bash
python nlp/intent_parser.py
```

### Test App Controller
```bash
python actions/apps.py
```

### Test System Controller
```bash
python actions/system.py
```

## 📊 Supported Intents

| Intent | Example Command | Action |
|--------|----------------|--------|
| OPEN_APP | "open firefox" | Launch application |
| CLOSE_APP | "close chrome" | Terminate application |
| SEARCH | "search for cats" | Web search |
| PLAY_MUSIC | "play music" | Open music player |
| SET_TIMER | "timer for 5 minutes" | Set countdown timer ✨ NEW |
| GET_WEATHER | "what's the weather" | Weather search |
| GET_TIME | "what time is it" | Show current time |
| VOLUME_UP | "volume up" | Increase volume |
| VOLUME_DOWN | "volume down" | Decrease volume |
| MUTE | "mute" | Mute audio ✨ NEW |
| UNMUTE | "unmute" | Unmute audio ✨ NEW |
| LOCK_SCREEN | "lock screen" | Lock computer ✨ NEW |
| TAKE_SCREENSHOT | "take a screenshot" | Capture screen |
| PLAY_MEDIA | "play video" / "resume" | Play/resume media (VLC, YouTube, etc.) ✨ NEW |
| PAUSE_MEDIA | "pause video" | Pause media ✨ NEW |
| NEXT_TRACK | "next track" / "skip" | Skip to next track ✨ NEW |
| PREVIOUS_TRACK | "previous track" / "back" | Go to previous track ✨ NEW |
| CALCULATE | "calculate 23 * 45" | Quick math calculations ✨ NEW |
| SHUTDOWN | "shutdown" | Power off (with confirmation) |

## 🛠️ Troubleshooting

### No Microphone Detected
```bash
python test_microphone.py
```
Check if sounddevice detects your microphone.

### Speech Recognition Not Working
1. Check internet connection (uses Google Speech API)
2. Speak clearly and close to microphone
3. Adjust ambient noise: The system auto-adjusts on startup

### Commands Not Executing
1. Check if intent is recognized correctly
2. Verify application names (e.g., "firefox" not "Firefox")
3. Check system permissions

## 🔐 Privacy

- Speech recognition uses Google Speech API (requires internet)
- Audio is sent to Google for processing
- No audio is stored locally
- For offline use, consider implementing local speech recognition

## 🚧 Known Limitations

- Wake word detection requires PyAudio (not available for Python 3.14 yet)
- Speech recognition requires internet connection
- Some system commands may need administrator privileges

## 🎓 Development

### Add New Intent
1. Add intent type to `nlp/intent_parser.py`
2. Add pattern matching rules
3. Add handler in `toc/dispatcher.py`
4. Implement action in `actions/` modules

### Add New Action
1. Create method in appropriate controller
2. Add dispatcher handler
3. Update intent parser if needed

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Run system tests
3. Create GitHub issue with details

---

**Status:** ✅ Fully Functional
**Voice Input:** ✅ Working (sounddevice)
**Text Input:** ✅ Working
**GUI:** ✅ Working
**Action Execution:** ✅ Working

**Start using:** `python run_assistant.py`

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
- (Optional) Local LLM runtime (e.g. Ollama) for personalized chat

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

3. **(Optional) Install as Windows startup app (hands-free mode)**
   ```bash
   python install_startup.py
   ```
   This will create a startup entry that launches the hands-free wake-word assistant automatically when you log in to Windows.

4. **Start the assistant manually (if you don't use startup)**
   ```bash
   python main.py
   ```

5. **(Optional) Enable local LLM for chat**
- Install [Ollama](https://ollama.com) and pull a model, for example:
  ```bash
  ollama pull llama3.2
  ```
- Optionally set:
  ```bash
  set LLM_MODEL=llama3.2
  set LLM_BASE_URL=http://localhost:11434
  ```
The assistant will then use the local LLM for open-ended, personalized conversation and as a fallback when a command intent is not recognized.

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