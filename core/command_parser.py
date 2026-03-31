"""
JARVIS Command Parser
Hybrid system: keyword matching → PC control, fallback → AI brain.
Uses intent detection to route commands intelligently.
"""

import re
import logging
from typing import Tuple, Optional
from enum import Enum, auto

logger = logging.getLogger(__name__)


class CommandType(Enum):
    # PC Control
    OPEN_APP = auto()
    OPEN_URL = auto()
    SEARCH_WEB = auto()
    OPEN_FOLDER = auto()
    SCREENSHOT = auto()
    SYSTEM_STATUS = auto()
    SHUTDOWN = auto()
    RESTART = auto()
    SHOW_TIME = auto()
    SHOW_DATE = auto()
    RUN_SCRIPT = auto()

    # Memory
    REMEMBER = auto()
    RECALL = auto()
    FORGET = auto()
    SHOW_NOTES = auto()

    # Voice
    VOICE_ON = auto()
    VOICE_OFF = auto()
    TTS_ON = auto()
    TTS_OFF = auto()

    # System
    CLEAR_MEMORY = auto()
    SHOW_HISTORY = auto()
    HELP = auto()
    SETTINGS = auto()
    EXIT = auto()

    # AI fallback
    AI_QUERY = auto()

    # Unknown
    UNKNOWN = auto()


class ParsedCommand:
    def __init__(self, cmd_type: CommandType, raw: str, args: dict = None):
        self.type = cmd_type
        self.raw = raw
        self.args = args or {}

    def __repr__(self):
        return f"ParsedCommand(type={self.type.name}, args={self.args})"


class CommandParser:
    """
    Routes user input to the correct handler.
    Priority: exact keywords → pattern matching → AI fallback.
    """

    # App name → executable mapping (Windows)
    APP_MAP = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "notepad": "notepad.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "files": "explorer.exe",
        "vscode": "code.exe",
        "vs code": "code.exe",
        "visual studio code": "code.exe",
        "code": "code.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "terminal": "cmd.exe",
        "powershell": "powershell.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "task manager": "taskmgr.exe",
        "taskmanager": "taskmgr.exe",
        "control panel": "control.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "slack": "slack.exe",
        "vlc": "vlc.exe",
        "snipping tool": "SnippingTool.exe",
    }

    # URL patterns
    URL_MAP = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "stack overflow": "https://stackoverflow.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "linkedin": "https://linkedin.com",
        "reddit": "https://reddit.com",
        "amazon": "https://amazon.com",
        "netflix": "https://netflix.com",
        "wikipedia": "https://wikipedia.org",
        "maps": "https://maps.google.com",
        "google maps": "https://maps.google.com",
        "chatgpt": "https://chat.openai.com",
        "claude": "https://claude.ai",
    }

    def parse(self, raw_input: str) -> ParsedCommand:
        """Main parse entry point. Returns a ParsedCommand."""
        text = raw_input.strip()
        if not text:
            return ParsedCommand(CommandType.UNKNOWN, raw_input)

        lower = text.lower().strip()

        # --- Exit / Quit ---
        if lower in ("exit", "quit", "bye", "goodbye", "close jarvis"):
            return ParsedCommand(CommandType.EXIT, raw_input)

        # --- Help ---
        if lower in ("help", "?", "commands", "what can you do"):
            return ParsedCommand(CommandType.HELP, raw_input)

        # --- Time / Date ---
        if re.search(r"\b(time|clock)\b", lower) and re.search(r"\b(what|show|tell|current)\b", lower):
            return ParsedCommand(CommandType.SHOW_TIME, raw_input)
        if lower in ("time", "show time", "current time", "what time"):
            return ParsedCommand(CommandType.SHOW_TIME, raw_input)
        if re.search(r"\b(date|today|day)\b", lower) and re.search(r"\b(what|show|tell|current)\b", lower):
            return ParsedCommand(CommandType.SHOW_DATE, raw_input)
        if lower in ("date", "show date", "what date", "today"):
            return ParsedCommand(CommandType.SHOW_DATE, raw_input)

        # --- System Status ---
        if re.search(r"\b(system|cpu|ram|memory|disk|performance|status|resources)\b", lower):
            if re.search(r"\b(show|check|status|usage|monitor|how|what)\b", lower):
                return ParsedCommand(CommandType.SYSTEM_STATUS, raw_input)
        if lower in ("status", "system status", "system info"):
            return ParsedCommand(CommandType.SYSTEM_STATUS, raw_input)

        # --- Screenshot ---
        if re.search(r"\b(screenshot|capture|screen|snap)\b", lower):
            return ParsedCommand(CommandType.SCREENSHOT, raw_input)

        # --- Shutdown / Restart ---
        if re.search(r"\b(shutdown|shut down|power off|turn off)\b", lower):
            return ParsedCommand(CommandType.SHUTDOWN, raw_input)
        if re.search(r"\b(restart|reboot|reset)\b", lower):
            return ParsedCommand(CommandType.RESTART, raw_input)

        # --- Memory: REMEMBER ---
        remember_match = re.search(
            r"(?:remember|note|save|store)\s+(?:that\s+)?(?:my\s+)?(?:name\s+is\s+)?(.+)",
            lower
        )
        if remember_match:
            note_text = raw_input[remember_match.start(1):]
            return ParsedCommand(CommandType.REMEMBER, raw_input, {"note": note_text.strip()})

        # --- Memory: RECALL ---
        if re.search(r"\b(recall|what did i|what do you remember|my notes|show notes|show memory)\b", lower):
            return ParsedCommand(CommandType.RECALL, raw_input)
        if lower in ("notes", "memories", "remember", "show notes"):
            return ParsedCommand(CommandType.SHOW_NOTES, raw_input)

        # --- Forget ---
        if re.search(r"\b(forget|clear notes|delete notes)\b", lower):
            return ParsedCommand(CommandType.FORGET, raw_input)

        # --- Voice Controls ---
        if re.search(r"\b(voice|mic|microphone)\b", lower) and re.search(r"\b(on|enable|start|activate)\b", lower):
            return ParsedCommand(CommandType.VOICE_ON, raw_input)
        if re.search(r"\b(voice|mic|microphone)\b", lower) and re.search(r"\b(off|disable|stop|deactivate)\b", lower):
            return ParsedCommand(CommandType.VOICE_OFF, raw_input)
        if re.search(r"\b(speak|tts|text.to.speech|read aloud)\b", lower) and re.search(r"\b(on|enable)\b", lower):
            return ParsedCommand(CommandType.TTS_ON, raw_input)
        if re.search(r"\b(speak|tts|text.to.speech|read aloud)\b", lower) and re.search(r"\b(off|disable)\b", lower):
            return ParsedCommand(CommandType.TTS_OFF, raw_input)

        # --- Clear Memory ---
        if re.search(r"\b(clear|reset|forget)\b", lower) and re.search(r"\b(history|conversation|context|memory)\b", lower):
            return ParsedCommand(CommandType.CLEAR_MEMORY, raw_input)

        # --- Show History ---
        if re.search(r"\b(history|conversation|chat log)\b", lower):
            return ParsedCommand(CommandType.SHOW_HISTORY, raw_input)

        # --- Settings ---
        if lower in ("settings", "config", "configure", "preferences", "setup"):
            return ParsedCommand(CommandType.SETTINGS, raw_input)

        # --- Search Web ---
        search_match = re.search(
            r"(?:search|find|look up|google|look for|search for)\s+(?:for\s+)?[\"']?(.+?)[\"']?\s*$",
            lower
        )
        if search_match:
            query = raw_input[raw_input.lower().find(search_match.group(1)):]
            return ParsedCommand(CommandType.SEARCH_WEB, raw_input, {"query": query.strip()})

        # Natural language search: "cheapest flights from X to Y"
        if re.search(r"\b(flight|hotel|price|weather|forecast|cheapest|best deal)\b", lower):
            return ParsedCommand(CommandType.SEARCH_WEB, raw_input, {"query": text})

        # --- Open URL ---
        for keyword, url in self.URL_MAP.items():
            pattern = rf"\b(open|go to|launch|visit|navigate to)\b.*\b{re.escape(keyword)}\b"
            if re.search(pattern, lower) or lower in (keyword, f"open {keyword}"):
                return ParsedCommand(CommandType.OPEN_URL, raw_input, {"url": url, "name": keyword})

        # --- Open App ---
        for app_name, executable in self.APP_MAP.items():
            pattern = rf"\b(open|launch|start|run)\b.*\b{re.escape(app_name)}\b"
            if re.search(pattern, lower) or lower in (app_name, f"open {app_name}", f"launch {app_name}"):
                return ParsedCommand(CommandType.OPEN_APP, raw_input, {"app": app_name, "exe": executable})

        # --- Open Folder ---
        folder_match = re.search(r"(?:open|navigate to|go to)\s+(?:folder\s+)?(.+)", lower)
        if folder_match and re.search(r"\b(folder|directory|path|drive)\b", lower):
            folder = raw_input[raw_input.lower().find(folder_match.group(1)):]
            return ParsedCommand(CommandType.OPEN_FOLDER, raw_input, {"path": folder.strip()})

        # --- AI Fallback ---
        return ParsedCommand(CommandType.AI_QUERY, raw_input)
