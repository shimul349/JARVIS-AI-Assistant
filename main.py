"""
JARVIS - Just A Rather Very Intelligent System
Main Entry Point
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config
from gui.app import JarvisApp


def main():
    """Launch JARVIS."""
    print("Initializing JARVIS...")
    config = Config()
    app = JarvisApp(config)
    app.run()


if __name__ == "__main__":
    main()
