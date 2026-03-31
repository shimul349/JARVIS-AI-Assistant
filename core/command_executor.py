"""
JARVIS Command Executor
Orchestrates: Parser → PC Controller / Memory / AI Brain.
Central hub that all commands flow through.
"""

import logging
from typing import Tuple, Callable, Optional
from core.command_parser import CommandParser, CommandType, ParsedCommand
from core.pc_controller import PCController
from core.ai_brain import AIBrain
from core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Receives parsed commands and dispatches to correct module.
    Returns (response_text, requires_confirmation, confirmation_callback).
    """

    def __init__(self, config):
        self.config = config
        self.parser = CommandParser()
        self.pc = PCController(config)
        self.brain = AIBrain(config)
        self.memory = MemoryManager(config)

    def execute(self, raw_input: str) -> dict:
        """
        Main execution pipeline.

        Returns a result dict:
        {
            "text": str,               # Response to display
            "confirm": bool,           # Does this need user confirmation?
            "confirm_action": callable # Call this if user confirms
            "confirm_msg": str         # What to ask the user
        }
        """
        raw_input = raw_input.strip()
        if not raw_input:
            return self._result("Please type a command or question.")

        cmd = self.parser.parse(raw_input)
        logger.info(f"Parsed: {cmd}")

        return self._dispatch(cmd)

    def _dispatch(self, cmd: ParsedCommand) -> dict:
        t = cmd.type

        # ── Time / Date ────────────────────────────────────────────────────
        if t == CommandType.SHOW_TIME:
            return self._result(self.pc.get_time())

        if t == CommandType.SHOW_DATE:
            return self._result(self.pc.get_date())

        # ── System Status ──────────────────────────────────────────────────
        if t == CommandType.SYSTEM_STATUS:
            return self._result(self.pc.get_system_status())

        # ── Screenshot ─────────────────────────────────────────────────────
        if t == CommandType.SCREENSHOT:
            ok, msg = self.pc.take_screenshot()
            return self._result(msg)

        # ── App Launch ─────────────────────────────────────────────────────
        if t == CommandType.OPEN_APP:
            ok, msg = self.pc.open_application(cmd.args["app"], cmd.args["exe"])
            return self._result(msg)

        # ── Open URL ───────────────────────────────────────────────────────
        if t == CommandType.OPEN_URL:
            ok, msg = self.pc.open_url(cmd.args["url"], cmd.args.get("name", ""))
            return self._result(msg)

        # ── Web Search ─────────────────────────────────────────────────────
        if t == CommandType.SEARCH_WEB:
            query = cmd.args.get("query", cmd.raw)
            ok, msg = self.pc.search_web(query)
            return self._result(msg)

        # ── Open Folder ────────────────────────────────────────────────────
        if t == CommandType.OPEN_FOLDER:
            ok, msg = self.pc.open_folder(cmd.args.get("path", ""))
            return self._result(msg)

        # ── Shutdown (CONFIRMATION REQUIRED) ───────────────────────────────
        if t == CommandType.SHUTDOWN:
            if not self.config.require_confirmation_for_shutdown:
                ok, msg = self.pc.shutdown_system()
                return self._result(msg)
            return self._result(
                "⚠️ You've requested a SYSTEM SHUTDOWN.",
                confirm=True,
                confirm_msg="Are you sure you want to shut down the computer?",
                confirm_action=lambda: self.pc.shutdown_system()[1]
            )

        # ── Restart (CONFIRMATION REQUIRED) ────────────────────────────────
        if t == CommandType.RESTART:
            if not self.config.require_confirmation_for_restart:
                ok, msg = self.pc.restart_system()
                return self._result(msg)
            return self._result(
                "⚠️ You've requested a SYSTEM RESTART.",
                confirm=True,
                confirm_msg="Are you sure you want to restart the computer?",
                confirm_action=lambda: self.pc.restart_system()[1]
            )

        # ── Memory: Remember ───────────────────────────────────────────────
        if t == CommandType.REMEMBER:
            note = cmd.args.get("note", cmd.raw)
            msg = self.memory.remember(note)
            return self._result(msg)

        # ── Memory: Recall ─────────────────────────────────────────────────
        if t in (CommandType.RECALL, CommandType.SHOW_NOTES):
            return self._result(self.memory.recall_all())

        # ── Memory: Forget ─────────────────────────────────────────────────
        if t == CommandType.FORGET:
            return self._result(
                "⚠️ You want to clear all saved notes.",
                confirm=True,
                confirm_msg="Delete all saved notes? This cannot be undone.",
                confirm_action=lambda: self.memory.forget_all()
            )

        # ── Voice Toggles ──────────────────────────────────────────────────
        if t == CommandType.VOICE_ON:
            self.config.voice_enabled = True
            self.config.save()
            return self._result("🎙️ Voice input enabled. Say your wake word to activate.")

        if t == CommandType.VOICE_OFF:
            self.config.voice_enabled = False
            self.config.save()
            return self._result("🔇 Voice input disabled.")

        if t == CommandType.TTS_ON:
            self.config.tts_enabled = True
            self.config.save()
            return self._result("🔊 Text-to-speech enabled.")

        if t == CommandType.TTS_OFF:
            self.config.tts_enabled = False
            self.config.save()
            return self._result("🔇 Text-to-speech disabled.")

        # ── Conversation Memory ────────────────────────────────────────────
        if t == CommandType.CLEAR_MEMORY:
            self.brain.clear_memory()
            return self._result("🧹 Conversation memory cleared. Starting fresh.")

        if t == CommandType.SHOW_HISTORY:
            return self._result(self.brain.get_history_summary())

        # ── Help ───────────────────────────────────────────────────────────
        if t == CommandType.HELP:
            return self._result(self._help_text())

        # ── Settings ───────────────────────────────────────────────────────
        if t == CommandType.SETTINGS:
            return self._result("⚙️ Settings panel", settings=True)

        # ── Exit ───────────────────────────────────────────────────────────
        if t == CommandType.EXIT:
            return self._result("Goodbye. JARVIS signing off.", exit=True)

        # ── AI Fallback ────────────────────────────────────────────────────
        if t == CommandType.AI_QUERY:
            notes_context = self.memory.get_notes_as_context()
            response = self.brain.think(cmd.raw, context=notes_context if notes_context else None)
            return self._result(response, source="ai")

        return self._result("I didn't understand that command. Type 'help' for options.")

    def _result(self, text: str, confirm: bool = False, confirm_msg: str = "",
                confirm_action=None, exit: bool = False, settings: bool = False,
                source: str = "system") -> dict:
        return {
            "text": text,
            "confirm": confirm,
            "confirm_msg": confirm_msg,
            "confirm_action": confirm_action,
            "exit": exit,
            "settings": settings,
            "source": source,  # "system" | "ai"
        }

    def _help_text(self) -> str:
        return """
─── JARVIS Command Reference ────────────────────────────────────

  📱 APP CONTROL
     open chrome / firefox / vscode / notepad / calculator
     open youtube / google / gmail / github / spotify

  🔍 WEB & SEARCH
     search [query]
     search cheapest flights from Dhaka to Dubai
     open google / youtube / reddit

  📁 FILE SYSTEM
     open folder downloads / desktop / documents
     open folder C:\\Users\\YourName\\Projects

  📸 SYSTEM
     screenshot          — capture desktop
     system status       — CPU, RAM, disk usage
     time / date         — current time and date

  🧠 MEMORY
     remember [text]     — save a note
     recall / notes      — show all saved notes
     forget              — clear all notes

  🎙️ VOICE (OPTIONAL)
     voice on / off      — toggle microphone input
     speak on / off      — toggle text-to-speech

  💬 CONVERSATION
     clear memory        — reset AI conversation context
     history             — show recent AI conversation

  ⚙️ SETTINGS
     settings            — open settings panel

  ❓ ANYTHING ELSE → Sent to AI Brain (ChatGPT)

─────────────────────────────────────────────────────────────────
""".strip()
