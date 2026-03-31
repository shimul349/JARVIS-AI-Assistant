"""
JARVIS Clipboard Monitor (OPTIONAL / TOGGLEABLE)
Watches clipboard for changes and optionally processes content.
"""

import logging
import threading
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ClipboardMonitor:
    """
    Polls clipboard for changes. Notifies callback on new content.
    Can be toggled on/off at runtime.
    """

    def __init__(self, config, on_change_callback: Optional[Callable] = None):
        self.config = config
        self.on_change = on_change_callback
        self._running = False
        self._thread = None
        self._last_content = ""
        self.available = False

        try:
            import pyperclip
            self.available = True
        except ImportError:
            logger.warning("pyperclip not installed. Clipboard monitor unavailable.")

    def start(self):
        if not self.available or self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("Clipboard monitor started.")

    def stop(self):
        self._running = False
        logger.info("Clipboard monitor stopped.")

    def _poll_loop(self):
        import pyperclip
        while self._running:
            try:
                current = pyperclip.paste()
                if current != self._last_content and current.strip():
                    self._last_content = current
                    if self.on_change:
                        self.on_change(current)
            except Exception:
                pass
            time.sleep(1)

    def get_current(self) -> str:
        """Return current clipboard content."""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return ""
