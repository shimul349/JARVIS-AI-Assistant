# ◉ JARVIS — AI Desktop Assistant
### Just A Rather Very Intelligent System
> A production-grade, keyboard-first AI desktop assistant powered by OpenAI GPT.  
> Inspired by Iron Man's JARVIS. Safe. Modular. Expandable.

---

## 📁 Project Structure

```
jarvis/
├── main.py                    # Entry point — run this
├── setup.py                   # One-time setup wizard
├── config.json                # User settings (auto-generated)
├── requirements.txt           # Dependencies
│
├── core/                      # Business logic (no GUI dependencies)
│   ├── config.py              # Configuration loader
│   ├── ai_brain.py            # OpenAI GPT integration + memory
│   ├── command_parser.py      # Keyword + NLP intent routing
│   ├── command_executor.py    # Orchestrates all modules
│   ├── pc_controller.py       # Safe system operations
│   └── memory_manager.py      # Persistent notes storage
│
├── gui/
│   └── app.py                 # Tkinter dark-themed GUI
│
├── modules/                   # Optional plugin modules
│   ├── voice_module.py        # STT + TTS (optional)
│   └── clipboard_monitor.py   # Clipboard watcher (optional)
│
└── data/                      # Auto-created at runtime
    ├── memory.json            # Conversation state
    ├── notes.json             # User's saved notes
    ├── screenshots/           # Captured screenshots
    └── logs/                  # Application logs
```

---

## ⚙️ Setup Guide (Step by Step)

### Step 1 — Prerequisites
- Python **3.9 or higher** (download from python.org)
- pip (comes with Python)
- Windows 10/11 recommended (also works on macOS/Linux)

### Step 2 — Download / Clone
```bash
# If you have git:
git clone https://github.com/yourname/jarvis.git
cd jarvis

# Or just extract the ZIP to a folder and cd into it
```

### Step 3 — Run the Setup Wizard (Recommended)
```bash
python setup.py
```
The wizard will:
- Check your Python version
- Install all required packages
- Optionally install voice support
- Ask for your OpenAI API key
- Create a `launch_jarvis.bat` launcher (Windows)

### Step 4 — Manual Install (Alternative)
```bash
# Core only (no voice)
pip install openai psutil pyautogui Pillow

# With voice support
pip install openai psutil pyautogui Pillow SpeechRecognition pyttsx3 pyaudio

# Windows: if pyaudio fails
pip install pipwin
pipwin install pyaudio
```

### Step 5 — Add your OpenAI API Key
Either:
- **During setup.py** (recommended)
- **In-app**: Launch JARVIS → click ⚙ Settings → paste key → Save
- **Manually**: Edit `config.json`, set `"openai_api_key": "sk-..."`

Get your key at: https://platform.openai.com/api-keys

### Step 6 — Launch JARVIS
```bash
python main.py
# or double-click launch_jarvis.bat on Windows
```

---

## 🧠 How the Hybrid Command System Works

```
User Input
    │
    ▼
CommandParser.parse(input)
    │
    ├─ Keyword / Pattern Match ──► PC Controller (instant, no API)
    │     open chrome             open_application()
    │     search flights          search_web()
    │     system status           get_system_status()
    │     screenshot              take_screenshot()
    │     remember [note]         memory.remember()
    │
    └─ No match found ──────────► AI Brain (OpenAI GPT)
                                   brain.think(input, context=notes)
                                   Returns intelligent response
```

**Priority chain:**
1. Exact keyword → instant local execution  
2. Regex pattern → PC action  
3. Unknown intent → GPT with full conversation context  

This means: low latency for common commands, full AI intelligence for everything else.

---

## 💬 Command Examples

### App Control
```
open chrome
open vscode
open calculator
launch notepad
```

### Web & Search
```
open youtube
open google
search cheapest flights from Dhaka to Dubai
search weather in London tomorrow
find best laptop under $1000
```

### System
```
time                    → current time
date                    → today's date
system status           → CPU, RAM, disk usage
screenshot              → capture desktop
shutdown                → (requires confirmation)
restart                 → (requires confirmation)
```

### Memory / Notes
```
remember my project deadline is June 15
remember the API endpoint is https://api.example.com/v2
notes                   → show all saved notes
recall                  → same as notes
forget                  → clear all notes (confirms first)
```

### Folders
```
open folder downloads
open folder desktop
open folder C:\Users\You\Projects
```

### Voice (Optional)
```
voice on        → enable background wake word listening
voice off       → disable voice
speak on        → enable text-to-speech for AI responses
speak off       → disable TTS
```

### Conversation
```
clear memory    → reset AI conversation context
history         → show recent AI conversation log
help            → full command reference
settings        → open settings panel
exit / quit     → close JARVIS
```

### AI Brain (anything else)
```
what is the capital of Bangladesh?
explain quantum computing simply
write a Python function to sort a list
what should I eat for dinner tonight?
translate "hello world" to French
```

---

## 🔒 Safety System

| Action | Behavior |
|--------|----------|
| Shutdown PC | ⚠️ Confirmation dialog required |
| Restart PC | ⚠️ Confirmation dialog required |
| Delete notes | ⚠️ Confirmation dialog required |
| Open apps | ✅ Whitelist-only, no arbitrary shell exec |
| Web search | ✅ Uses browser, never executes server-side code |
| File access | ✅ Read-only, only opens folders in Explorer |
| AI responses | ✅ Never auto-executes AI-suggested commands |

---

## 🎙️ Voice Module (Optional)

The voice module is completely optional and modular:

```python
# Disabled by default in config.json
"voice_enabled": false,
"tts_enabled": false,
"wake_word": "jarvis"
```

**To use voice:**
1. Install: `pip install SpeechRecognition pyttsx3 pyaudio`
2. Enable in Settings or type `voice on`
3. Say "**jarvis** open chrome" to trigger commands

Voice module does NOT affect any other functionality when disabled.

---

## 🔧 Configuration Reference (`config.json`)

```json
{
  "openai_api_key": "sk-...",       // Your OpenAI key
  "ai_model": "gpt-4o",            // Model to use
  "ai_temperature": 0.7,           // Creativity (0.0-1.0)
  "voice_enabled": false,          // Voice input on/off
  "tts_enabled": false,            // Speech output on/off
  "wake_word": "jarvis",           // Wake word for voice
  "require_confirmation_for_shutdown": true,
  "require_confirmation_for_restart": true,
  "theme": "dark"
}
```

---

## 🚀 Extending JARVIS

### Add a new command keyword
Edit `core/command_parser.py`:
```python
# In APP_MAP dict:
"zoom": "Zoom.exe",

# In URL_MAP dict:
"notion": "https://notion.so",

# Add new command type in CommandType enum:
OPEN_TERMINAL = auto()

# Add pattern matching in parse() method
```

### Add a new module
1. Create `modules/my_module.py`
2. Import and instantiate in `core/command_executor.py`
3. Add handler in `_dispatch()` method

### Change AI personality
Edit `core/config.py` → `ai_system_prompt` string.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| GUI | Tkinter (built-in) |
| AI | OpenAI GPT-4o |
| System | psutil, subprocess |
| Screenshots | pyautogui / Pillow |
| Voice STT | SpeechRecognition + Google |
| Voice TTS | pyttsx3 |
| Storage | JSON files (local) |

---

## 🛣️ Roadmap (Commercial Expansion)

- [ ] Plugin marketplace system
- [ ] Multi-user profiles
- [ ] Cloud memory sync
- [ ] Custom wake words (offline, e.g. Whisper)
- [ ] File content search (Whoosh/SQLite FTS)
- [ ] Email integration
- [ ] Calendar / task management
- [ ] System tray mode (minimized to tray)
- [ ] Hotkey global shortcut (e.g. Ctrl+Space)
- [ ] Packaging as .exe installer (PyInstaller)

---

*JARVIS v1.0 — Built for expansion into a commercial AI product.*
