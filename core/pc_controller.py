"""
JARVIS PC Controller
Handles all safe system interactions: launching apps, screenshots,
system info, folder navigation. All destructive actions require confirmation.
"""

import os
import sys
import platform
import subprocess
import logging
import datetime
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


class PCController:
    """
    Safe PC control layer. Only executes whitelisted operations.
    Destructive commands return (False, confirmation_message) for the GUI to confirm.
    """

    def __init__(self, config):
        self.config = config
        self.screenshot_dir = Path(config.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    # ─── APP LAUNCHING ────────────────────────────────────────────────────────

    def open_application(self, app_name: str, executable: str) -> Tuple[bool, str]:
        """Launch an application by executable name."""
        try:
            if IS_WINDOWS:
                # Try direct name first (relies on PATH), then 'start' command
                try:
                    subprocess.Popen([executable], shell=False)
                except FileNotFoundError:
                    subprocess.Popen(f'start "" "{executable}"', shell=True)
            elif IS_MAC:
                mac_name = app_name.title()
                subprocess.Popen(["open", "-a", mac_name])
            else:
                # Linux: try common names
                subprocess.Popen([app_name.lower()])

            return True, f"✅ Opening {app_name.title()}..."

        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return False, f"❌ Could not open '{app_name}'. Make sure it's installed."

    def open_url(self, url: str, name: str = "") -> Tuple[bool, str]:
        """Open a URL in the default browser."""
        try:
            import webbrowser
            webbrowser.open(url)
            label = name or url
            return True, f"🌐 Opening {label} in your browser..."
        except Exception as e:
            return False, f"❌ Failed to open URL: {e}"

    def search_web(self, query: str) -> Tuple[bool, str]:
        """Perform a Google search with the given query."""
        try:
            import webbrowser
            from urllib.parse import quote_plus
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            webbrowser.open(search_url)
            return True, f"🔍 Searching Google for: \"{query}\""
        except Exception as e:
            return False, f"❌ Search failed: {e}"

    def open_folder(self, path: str) -> Tuple[bool, str]:
        """Open a folder in File Explorer / Finder / Nautilus."""
        expanded = os.path.expandvars(os.path.expanduser(path))
        folder = Path(expanded)

        if not folder.exists():
            # Try some common shortcuts
            shortcuts = {
                "desktop": Path.home() / "Desktop",
                "documents": Path.home() / "Documents",
                "downloads": Path.home() / "Downloads",
                "pictures": Path.home() / "Pictures",
                "music": Path.home() / "Music",
                "videos": Path.home() / "Videos",
                "home": Path.home(),
            }
            for key, val in shortcuts.items():
                if key in path.lower():
                    folder = val
                    break
            else:
                return False, f"❌ Folder not found: {path}"

        try:
            if IS_WINDOWS:
                subprocess.Popen(["explorer", str(folder)])
            elif IS_MAC:
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
            return True, f"📁 Opening folder: {folder}"
        except Exception as e:
            return False, f"❌ Could not open folder: {e}"

    # ─── SCREENSHOTS ──────────────────────────────────────────────────────────

    def take_screenshot(self) -> Tuple[bool, str]:
        """Capture the full desktop screenshot."""
        try:
            import pyautogui
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filename))
            return True, f"📸 Screenshot saved: {filename.name}"
        except ImportError:
            # Fallback: use PIL if available
            try:
                from PIL import ImageGrab
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
                img = ImageGrab.grab()
                img.save(str(filename))
                return True, f"📸 Screenshot saved: {filename.name}"
            except Exception as e:
                return False, f"❌ Screenshot failed. Install pyautogui: pip install pyautogui\nError: {e}"
        except Exception as e:
            return False, f"❌ Screenshot failed: {e}"

    # ─── SYSTEM INFO ──────────────────────────────────────────────────────────

    def get_system_status(self) -> str:
        """Return formatted system resource information."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()

            ram_used = ram.used / (1024 ** 3)
            ram_total = ram.total / (1024 ** 3)
            disk_used = disk.used / (1024 ** 3)
            disk_total = disk.total / (1024 ** 3)

            lines = [
                "─── System Status ───────────────────",
                f"  CPU Usage   : {cpu:.1f}%",
                f"  RAM         : {ram_used:.1f} GB / {ram_total:.1f} GB ({ram.percent}%)",
                f"  Disk        : {disk_used:.1f} GB / {disk_total:.1f} GB ({disk.percent}%)",
            ]

            if battery:
                lines.append(f"  Battery     : {battery.percent:.0f}% {'🔌 Charging' if battery.power_plugged else '🔋 On Battery'}")

            # Top CPU processes
            procs = sorted(psutil.process_iter(["name", "cpu_percent"]),
                           key=lambda p: p.info.get("cpu_percent") or 0, reverse=True)[:3]
            if procs:
                lines.append("  Top Processes:")
                for p in procs:
                    lines.append(f"    • {p.info['name']} — {p.info.get('cpu_percent', 0):.1f}%")

            lines.append("─────────────────────────────────────")
            return "\n".join(lines)

        except ImportError:
            return "⚠️ psutil not installed. Run: pip install psutil"
        except Exception as e:
            return f"❌ Could not retrieve system status: {e}"

    # ─── TIME / DATE ──────────────────────────────────────────────────────────

    def get_time(self) -> str:
        now = datetime.datetime.now()
        return f"🕐 Current time: {now.strftime('%I:%M:%S %p')}"

    def get_date(self) -> str:
        now = datetime.datetime.now()
        return f"📅 Today is {now.strftime('%A, %B %d, %Y')}"

    # ─── SYSTEM ACTIONS (REQUIRE CONFIRMATION) ────────────────────────────────

    def shutdown_system(self) -> Tuple[bool, str]:
        """Shutdown the PC — must be confirmed by GUI before calling."""
        try:
            if IS_WINDOWS:
                subprocess.run(["shutdown", "/s", "/t", "5"])
            elif IS_MAC:
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            else:
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            return True, "⚠️ System shutting down in 5 seconds..."
        except Exception as e:
            return False, f"❌ Shutdown failed: {e}"

    def restart_system(self) -> Tuple[bool, str]:
        """Restart the PC — must be confirmed by GUI before calling."""
        try:
            if IS_WINDOWS:
                subprocess.run(["shutdown", "/r", "/t", "5"])
            elif IS_MAC:
                subprocess.run(["sudo", "shutdown", "-r", "now"])
            else:
                subprocess.run(["sudo", "reboot"])
            return True, "🔄 System restarting in 5 seconds..."
        except Exception as e:
            return False, f"❌ Restart failed: {e}"
