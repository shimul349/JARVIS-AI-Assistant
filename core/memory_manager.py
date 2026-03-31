"""
JARVIS Memory Module
Handles persistent note storage and retrieval.
Notes are stored as JSON locally.
"""

import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Persistent memory store. Saves user notes to disk.
    Short-term context is managed by AIBrain separately.
    """

    def __init__(self, config):
        self.notes_path = Path(__file__).parent.parent / config.notes_file
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        self.notes: List[Dict] = []
        self._load()

    def _load(self):
        """Load notes from disk."""
        if self.notes_path.exists():
            try:
                with open(self.notes_path) as f:
                    self.notes = json.load(f)
                logger.info(f"Loaded {len(self.notes)} notes from memory.")
            except Exception as e:
                logger.error(f"Failed to load notes: {e}")
                self.notes = []

    def _save(self):
        """Persist notes to disk."""
        try:
            with open(self.notes_path, "w") as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save notes: {e}")

    def remember(self, text: str) -> str:
        """Save a new note."""
        entry = {
            "id": len(self.notes) + 1,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self.notes.append(entry)
        self._save()
        logger.info(f"Remembered: {text}")
        return f"✅ Got it! I've saved: \"{text}\""

    def recall_all(self) -> str:
        """Return all saved notes formatted."""
        if not self.notes:
            return "🧠 No memories stored yet. Use 'remember [something]' to save notes."

        lines = ["─── Your Saved Notes ────────────────"]
        for note in self.notes[-20:]:  # Show last 20
            ts = note.get("timestamp", "")[:10]
            lines.append(f"  [{note['id']}] {note['text']}  ({ts})")
        lines.append("─────────────────────────────────────")
        return "\n".join(lines)

    def search_notes(self, query: str) -> str:
        """Search notes by keyword."""
        results = [n for n in self.notes if query.lower() in n["text"].lower()]
        if not results:
            return f"🔍 No notes found containing '{query}'."
        lines = [f"🔍 Found {len(results)} note(s) matching '{query}':"]
        for note in results:
            lines.append(f"  [{note['id']}] {note['text']}")
        return "\n".join(lines)

    def forget_all(self) -> str:
        """Clear all notes."""
        count = len(self.notes)
        self.notes = []
        self._save()
        return f"🗑️ Cleared {count} stored notes."

    def forget_by_id(self, note_id: int) -> str:
        """Delete a specific note by ID."""
        original = len(self.notes)
        self.notes = [n for n in self.notes if n["id"] != note_id]
        if len(self.notes) < original:
            self._save()
            return f"🗑️ Note #{note_id} deleted."
        return f"❌ Note #{note_id} not found."

    def get_notes_as_context(self) -> str:
        """Return notes as a string for AI context injection."""
        if not self.notes:
            return ""
        texts = [n["text"] for n in self.notes[-10:]]
        return "User's saved notes: " + "; ".join(texts)
