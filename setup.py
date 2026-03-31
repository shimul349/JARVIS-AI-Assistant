"""
JARVIS Setup Script
Run this once to install dependencies and verify your setup.
"""

import sys
import subprocess
import os
from pathlib import Path


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def check_python():
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required.")
        sys.exit(1)
    print("✅ Python version OK")


def install_packages(voice=False):
    core = ["openai", "psutil", "pyautogui", "Pillow"]
    voice_pkgs = ["SpeechRecognition", "pyttsx3"]

    packages = core[:]
    if voice:
        packages.extend(voice_pkgs)

    print(f"\nInstalling: {', '.join(packages)}")
    ok, out, err = run(f"{sys.executable} -m pip install {' '.join(packages)}")
    if ok:
        print("✅ Packages installed.")
    else:
        print(f"⚠️ Some packages failed. Error:\n{err}")

    if voice:
        print("\nInstalling pyaudio (voice input)...")
        ok, _, err = run(f"{sys.executable} -m pip install pyaudio")
        if not ok:
            print("⚠️ pyaudio failed. Try: pip install pipwin && pipwin install pyaudio")
        else:
            print("✅ pyaudio installed.")


def setup_api_key():
    print("\n── OpenAI API Key Setup ─────────────────────────────")
    print("Your API key is needed for the AI brain (ChatGPT).")
    print("Get one at: https://platform.openai.com/api-keys")
    print("Leave blank to skip (you can add it later in Settings).\n")

    key = input("Enter your OpenAI API key: ").strip()
    if key:
        import json
        config_path = Path("config.json")
        config = {}
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        config["openai_api_key"] = key
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ API key saved to config.json")
    else:
        print("⏭  Skipped. Add later via Settings menu in the app.")


def create_launcher():
    """Create a simple .bat launcher on Windows."""
    import platform
    if platform.system() == "Windows":
        bat = Path("launch_jarvis.bat")
        bat.write_text(f'@echo off\n"{sys.executable}" main.py\npause\n')
        print(f"✅ Created launcher: {bat.name}")


if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS Setup Wizard")
    print("=" * 50)

    check_python()

    voice = input("\nInstall voice support? (y/N): ").strip().lower() == "y"
    install_packages(voice)
    setup_api_key()
    create_launcher()

    print("\n" + "=" * 50)
    print("✅ Setup complete! Run JARVIS with:")
    print("   python main.py")
    print("=" * 50)
