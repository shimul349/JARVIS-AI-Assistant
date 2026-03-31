"""
JARVIS Configuration Module
Loads and manages all system settings from config.json or environment variables.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # API Keys
    openai_api_key: str = "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"

    # AI Settings
    ai_model: str = "gpt-4o"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1024
    ai_system_prompt: str = (
        "You are JARVIS, an advanced AI desktop assistant inspired by Iron Man's AI. "
        "You are intelligent, concise, and helpful. You assist the user with PC tasks, "
        "answer questions, provide information, and control applications. "
        "When asked to perform PC actions, describe what you would do clearly. "
        "Keep responses concise and professional. Address the user as 'Sir' or 'Ma'am' occasionally for character."
    )

    # Memory
    short_term_memory_limit: int = 20  # messages to keep in context
    memory_file: str = "data/memory.json"
    notes_file: str = "data/notes.json"

    # Voice (Optional)
    voice_enabled: bool = False
    tts_enabled: bool = False
    wake_word: str = "jarvis"
    voice_language: str = "en-US"

    # Safety
    require_confirmation_for_shutdown: bool = True
    require_confirmation_for_restart: bool = True
    require_confirmation_for_delete: bool = True
    whitelisted_apps: list = field(default_factory=lambda: [
        "chrome", "firefox", "edge", "notepad", "explorer",
        "code", "cmd", "powershell", "calculator", "paint",
        "word", "excel", "vlc", "spotify", "discord", "slack",
        "taskmanager", "control", "mspaint", "winword", "excel"
    ])

    # GUI
    theme: str = "dark"
    font_size: int = 13
    window_width: int = 900
    window_height: int = 700
    window_title: str = "JARVIS — AI Desktop Assistant"

    # Clipboard Monitor
    clipboard_monitor_enabled: bool = False

    # Screenshot save dir
    screenshot_dir: str = "data/screenshots"

    def __post_init__(self):
        self._load_from_file()
        self._load_from_env()
        self._ensure_directories()

    def _load_from_file(self):
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(self, k):
                    setattr(self, k, v)

    def _load_from_env(self):
        """Environment variables override config file."""
        if key := os.getenv("OPENAI_API_KEY"):
            self.openai_api_key = key

    def _ensure_directories(self):
        for path in ["data", "data/screenshots", "data/logs"]:
            Path(__file__).parent.parent.joinpath(path).mkdir(parents=True, exist_ok=True)

    def save(self):
        config_path = Path(__file__).parent.parent / "config.json"
        data = {
            "openai_api_key": self.openai_api_key,
            "ai_model": self.ai_model,
            "ai_temperature": self.ai_temperature,
            "voice_enabled": self.voice_enabled,
            "tts_enabled": self.tts_enabled,
            "wake_word": self.wake_word,
            "clipboard_monitor_enabled": self.clipboard_monitor_enabled,
            "theme": self.theme,
        }
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
