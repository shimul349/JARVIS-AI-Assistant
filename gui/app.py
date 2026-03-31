"""
JARVIS GUI Application
Dark-themed ChatGPT-style interface built with Tkinter.
Primary input: text. Voice: optional toggle.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import logging
import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Color Theme ──────────────────────────────────────────────────────────────
THEME = {
    "bg_dark":       "#0a0e1a",
    "bg_panel":      "#0f1525",
    "bg_input":      "#151d2e",
    "bg_msg_user":   "#1a2540",
    "bg_msg_ai":     "#0f1a2e",
    "bg_msg_system": "#101820",
    "accent":        "#00d4ff",
    "accent2":       "#0066ff",
    "accent_warn":   "#ff6b35",
    "text_primary":  "#e8f4f8",
    "text_secondary":"#8899aa",
    "text_accent":   "#00d4ff",
    "text_ai":       "#a8d8f0",
    "border":        "#1e2d45",
    "button_bg":     "#162035",
    "button_hover":  "#1e2d45",
    "green":         "#00ff88",
    "red":           "#ff4455",
}


class JarvisApp:
    def __init__(self, config):
        self.config = config
        self.executor = None
        self.voice_module = None
        self._voice_active = False

        self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._init_backend()
        self._show_welcome()

    def _setup_window(self):
        self.root.title(self.config.window_title)
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.root.minsize(700, 500)
        self.root.configure(bg=THEME["bg_dark"])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Try to set icon
        try:
            self.root.iconbitmap("assets/jarvis.ico")
        except Exception:
            pass

    def _build_ui(self):
        """Construct all UI elements."""
        # ── Top Bar ──────────────────────────────────────────────────────────
        top_bar = tk.Frame(self.root, bg=THEME["bg_panel"], height=50)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)

        # Logo / Title
        title_frame = tk.Frame(top_bar, bg=THEME["bg_panel"])
        title_frame.pack(side=tk.LEFT, padx=15)

        logo_dot = tk.Label(title_frame, text="◉", fg=THEME["accent"],
                            bg=THEME["bg_panel"], font=("Courier", 18))
        logo_dot.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(title_frame, text="JARVIS", fg=THEME["text_primary"],
                 bg=THEME["bg_panel"],
                 font=("Courier", 16, "bold")).pack(side=tk.LEFT)

        tk.Label(title_frame, text="  AI Desktop Assistant",
                 fg=THEME["text_secondary"], bg=THEME["bg_panel"],
                 font=("Courier", 10)).pack(side=tk.LEFT, pady=5)

        # Top-right controls
        controls = tk.Frame(top_bar, bg=THEME["bg_panel"])
        controls.pack(side=tk.RIGHT, padx=15)

        self.status_dot = tk.Label(controls, text="●", fg=THEME["green"],
                                   bg=THEME["bg_panel"], font=("Courier", 12))
        self.status_dot.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(controls, text="ONLINE",
                                     fg=THEME["green"], bg=THEME["bg_panel"],
                                     font=("Courier", 10))
        self.status_label.pack(side=tk.LEFT, padx=(0, 15))

        self._btn(controls, "⚙ Settings", self._open_settings).pack(side=tk.LEFT, padx=3)
        self._btn(controls, "🗑 Clear", self._clear_chat).pack(side=tk.LEFT, padx=3)

        # Separator
        tk.Frame(self.root, bg=THEME["accent"], height=1).pack(fill=tk.X)

        # ── Main Layout ───────────────────────────────────────────────────────
        main_frame = tk.Frame(self.root, bg=THEME["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = tk.Frame(main_frame, bg=THEME["bg_panel"], width=160)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="QUICK ACTIONS",
                 fg=THEME["text_secondary"], bg=THEME["bg_panel"],
                 font=("Courier", 8)).pack(pady=(15, 8))

        quick_cmds = [
            ("📊 Status", "system status"),
            ("🕐 Time", "time"),
            ("📸 Screenshot", "screenshot"),
            ("🧠 Notes", "recall"),
            ("🌐 Google", "open google"),
            ("📺 YouTube", "open youtube"),
            ("❓ Help", "help"),
        ]
        for label, cmd in quick_cmds:
            btn = tk.Button(
                sidebar, text=label, command=lambda c=cmd: self._quick_command(c),
                bg=THEME["button_bg"], fg=THEME["text_primary"],
                activebackground=THEME["button_hover"],
                activeforeground=THEME["accent"],
                font=("Courier", 9), relief=tk.FLAT,
                cursor="hand2", pady=6, anchor="w", padx=12
            )
            btn.pack(fill=tk.X, pady=1)

        # Voice toggle in sidebar
        tk.Frame(sidebar, bg=THEME["border"], height=1).pack(fill=tk.X, pady=10, padx=5)
        tk.Label(sidebar, text="VOICE MODULE",
                 fg=THEME["text_secondary"], bg=THEME["bg_panel"],
                 font=("Courier", 8)).pack(pady=(0, 5))

        self.voice_btn_var = tk.StringVar(value="🎙 Voice: OFF")
        self.voice_toggle_btn = tk.Button(
            sidebar, textvariable=self.voice_btn_var,
            command=self._toggle_voice,
            bg=THEME["button_bg"], fg=THEME["text_secondary"],
            activebackground=THEME["button_hover"],
            font=("Courier", 9), relief=tk.FLAT, cursor="hand2",
            pady=6, padx=8
        )
        self.voice_toggle_btn.pack(fill=tk.X, padx=5)

        self.tts_btn_var = tk.StringVar(value="🔊 TTS: OFF")
        self.tts_toggle_btn = tk.Button(
            sidebar, textvariable=self.tts_btn_var,
            command=self._toggle_tts,
            bg=THEME["button_bg"], fg=THEME["text_secondary"],
            activebackground=THEME["button_hover"],
            font=("Courier", 9), relief=tk.FLAT, cursor="hand2",
            pady=6, padx=8
        )
        self.tts_toggle_btn.pack(fill=tk.X, padx=5, pady=2)

        # System clock in sidebar bottom
        self.clock_label = tk.Label(sidebar, text="", fg=THEME["text_secondary"],
                                    bg=THEME["bg_panel"], font=("Courier", 10))
        self.clock_label.pack(side=tk.BOTTOM, pady=10)
        self._update_clock()

        # Separator
        tk.Frame(main_frame, bg=THEME["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ── Chat Area ─────────────────────────────────────────────────────────
        chat_frame = tk.Frame(main_frame, bg=THEME["bg_dark"])
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=THEME["bg_dark"],
            fg=THEME["text_primary"],
            font=("Courier", self.config.font_size),
            relief=tk.FLAT,
            state=tk.DISABLED,
            padx=16,
            pady=10,
            insertbackground=THEME["accent"],
            selectbackground=THEME["bg_msg_user"],
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=0)

        # Configure text tags for styling
        self.chat_display.tag_configure("user_label",
            foreground=THEME["accent"], font=("Courier", 10, "bold"))
        self.chat_display.tag_configure("user_text",
            foreground=THEME["text_primary"], font=("Courier", self.config.font_size))
        self.chat_display.tag_configure("ai_label",
            foreground=THEME["accent2"], font=("Courier", 10, "bold"))
        self.chat_display.tag_configure("ai_text",
            foreground=THEME["text_ai"], font=("Courier", self.config.font_size))
        self.chat_display.tag_configure("system_label",
            foreground=THEME["text_secondary"], font=("Courier", 10, "bold"))
        self.chat_display.tag_configure("system_text",
            foreground=THEME["text_secondary"], font=("Courier", self.config.font_size - 1))
        self.chat_display.tag_configure("warn_text",
            foreground=THEME["accent_warn"], font=("Courier", self.config.font_size))
        self.chat_display.tag_configure("success_text",
            foreground=THEME["green"], font=("Courier", self.config.font_size))
        self.chat_display.tag_configure("separator",
            foreground=THEME["border"])
        self.chat_display.tag_configure("timestamp",
            foreground=THEME["text_secondary"], font=("Courier", 9))

        # ── Input Bar ─────────────────────────────────────────────────────────
        tk.Frame(chat_frame, bg=THEME["border"], height=1).pack(fill=tk.X)

        input_frame = tk.Frame(chat_frame, bg=THEME["bg_input"], pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Prompt indicator
        tk.Label(input_frame, text=">_", fg=THEME["accent"],
                 bg=THEME["bg_input"], font=("Courier", 14, "bold")).pack(
            side=tk.LEFT, padx=(14, 6))

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent"],
            font=("Courier", self.config.font_size),
            relief=tk.FLAT,
            bd=0,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        self.input_entry.focus_set()

        # Send button
        send_btn = tk.Button(
            input_frame, text="SEND ↵",
            command=self._on_send,
            bg=THEME["accent2"], fg="white",
            activebackground=THEME["accent"],
            font=("Courier", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=6
        )
        send_btn.pack(side=tk.RIGHT, padx=(6, 14))

        # Voice mic button
        self.mic_btn = tk.Button(
            input_frame, text="🎙",
            command=self._on_mic_click,
            bg=THEME["button_bg"], fg=THEME["text_secondary"],
            activebackground=THEME["button_hover"],
            font=("Courier", 14),
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=4
        )
        self.mic_btn.pack(side=tk.RIGHT, padx=2)

        # ── Thinking indicator ────────────────────────────────────────────────
        self.thinking_var = tk.StringVar(value="")
        self.thinking_label = tk.Label(
            chat_frame, textvariable=self.thinking_var,
            fg=THEME["accent"], bg=THEME["bg_dark"],
            font=("Courier", 10)
        )
        self.thinking_label.pack(anchor="w", padx=20)

        # Command history
        self._cmd_history = []
        self._history_idx = -1

    def _btn(self, parent, text, command, **kwargs):
        return tk.Button(
            parent, text=text, command=command,
            bg=THEME["button_bg"], fg=THEME["text_secondary"],
            activebackground=THEME["button_hover"],
            activeforeground=THEME["text_primary"],
            font=("Courier", 9), relief=tk.FLAT, cursor="hand2",
            padx=8, pady=4, **kwargs
        )

    def _init_backend(self):
        """Initialize executor and optional modules in background."""
        def _init():
            from core.command_executor import CommandExecutor
            self.executor = CommandExecutor(self.config)
            logger.info("Backend initialized.")

            # Init voice module
            from modules.voice_module import VoiceModule
            self.voice_module = VoiceModule(
                self.config,
                on_speech_callback=self._on_voice_command
            )
            if self.config.voice_enabled:
                self.voice_module.start_listening()

        threading.Thread(target=_init, daemon=True).start()

    def _show_welcome(self):
        """Display welcome message."""
        now = datetime.datetime.now()
        hour = now.hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

        self._append_system(
            f"  ╔══════════════════════════════════════════════╗\n"
            f"  ║     JARVIS — AI Desktop Assistant  v1.0      ║\n"
            f"  ╚══════════════════════════════════════════════╝\n"
        )
        self._append_system(f"  {greeting}. JARVIS is online and ready.")
        self._append_system(f"  Type a command or question below. Type 'help' for commands.\n")

    # ─── Message Display ──────────────────────────────────────────────────────

    def _append_message(self, speaker: str, text: str, label_tag: str, text_tag: str):
        """Append a message block to the chat display."""
        self.chat_display.configure(state=tk.NORMAL)
        ts = datetime.datetime.now().strftime("%H:%M")

        self.chat_display.insert(tk.END, f"\n  {speaker}  ", label_tag)
        self.chat_display.insert(tk.END, f"[{ts}]\n", "timestamp")

        # Indent multi-line text
        for line in text.split("\n"):
            self.chat_display.insert(tk.END, f"  {line}\n", text_tag)

        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _append_user(self, text: str):
        self._append_message("YOU ›", text, "user_label", "user_text")

    def _append_ai(self, text: str):
        self._append_message("JARVIS ›", text, "ai_label", "ai_text")

    def _append_system(self, text: str, warn: bool = False):
        self.chat_display.configure(state=tk.NORMAL)
        tag = "warn_text" if warn else "system_text"
        for line in text.split("\n"):
            self.chat_display.insert(tk.END, f"  {line}\n", tag)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _set_thinking(self, active: bool):
        if active:
            self.thinking_var.set("  ◌ JARVIS is thinking...")
            self.input_entry.configure(state=tk.DISABLED)
        else:
            self.thinking_var.set("")
            self.input_entry.configure(state=tk.NORMAL)
            self.input_entry.focus_set()

    # ─── Input Handling ───────────────────────────────────────────────────────

    def _on_enter(self, event=None):
        self._on_send()

    def _on_send(self):
        text = self.input_var.get().strip()
        if not text:
            return

        self.input_var.set("")
        self._cmd_history.append(text)
        self._history_idx = -1

        self._append_user(text)

        if not self.executor:
            self._append_system("⏳ Still initializing... please wait a moment.")
            return

        self._set_thinking(True)

        def _run():
            result = self.executor.execute(text)
            self.root.after(0, lambda: self._handle_result(result))

        threading.Thread(target=_run, daemon=True).start()

    def _handle_result(self, result: dict):
        self._set_thinking(False)

        if result.get("exit"):
            self._append_system(result["text"])
            self.root.after(1000, self.root.destroy)
            return

        if result.get("confirm"):
            # Show confirmation dialog
            confirmed = messagebox.askyesno(
                "⚠️ Confirmation Required",
                result["confirm_msg"],
                icon="warning"
            )
            if confirmed and result.get("confirm_action"):
                action_result = result["confirm_action"]()
                if isinstance(action_result, str):
                    self._append_system(action_result, warn=True)
            else:
                self._append_system("Action cancelled.")
            return

        if result.get("settings"):
            self._open_settings()
            return

        text = result.get("text", "")
        source = result.get("source", "system")

        if source == "ai":
            self._append_ai(text)
        else:
            self._append_system(text)

        # TTS for AI responses
        if source == "ai" and self.config.tts_enabled and self.voice_module:
            self.voice_module.speak(text)

    def _quick_command(self, cmd: str):
        self.input_var.set(cmd)
        self._on_send()

    def _on_voice_command(self, text: str):
        """Called when voice module detects a command."""
        self.root.after(0, lambda: self._quick_command(text))

    def _on_mic_click(self):
        """Single voice capture on mic button click."""
        if not self.voice_module or not self.voice_module.available:
            self._append_system("⚠️ Voice module unavailable. Install: pip install SpeechRecognition pyaudio")
            return

        self.mic_btn.configure(fg=THEME["accent"], text="🔴")
        self._append_system("🎙️ Listening... speak now.")

        def _listen():
            text = self.voice_module.listen_once()
            self.root.after(0, lambda: self._on_voice_result(text))

        threading.Thread(target=_listen, daemon=True).start()

    def _on_voice_result(self, text: Optional[str]):
        self.mic_btn.configure(fg=THEME["text_secondary"], text="🎙")
        if text:
            self.input_var.set(text)
            self._on_send()
        else:
            self._append_system("Could not understand audio. Please try again.")

    # ─── Command History Navigation ───────────────────────────────────────────

    def _history_up(self, event=None):
        if not self._cmd_history:
            return
        if self._history_idx < len(self._cmd_history) - 1:
            self._history_idx += 1
        self.input_var.set(self._cmd_history[-(self._history_idx + 1)])

    def _history_down(self, event=None):
        if self._history_idx > 0:
            self._history_idx -= 1
            self.input_var.set(self._cmd_history[-(self._history_idx + 1)])
        else:
            self._history_idx = -1
            self.input_var.set("")

    # ─── Clock ────────────────────────────────────────────────────────────────

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=now)
        self.root.after(1000, self._update_clock)

    # ─── Toggles ─────────────────────────────────────────────────────────────

    def _toggle_voice(self):
        if not self.voice_module or not self.voice_module.available:
            self._append_system("⚠️ Voice module unavailable. Install: pip install SpeechRecognition pyaudio")
            return
        self.config.voice_enabled = not self.config.voice_enabled
        if self.config.voice_enabled:
            self.voice_module.start_listening()
            self.voice_btn_var.set("🎙 Voice: ON")
            self.voice_toggle_btn.configure(fg=THEME["accent"])
            self._append_system(f"🎙️ Voice listening activated. Say '{self.config.wake_word}' + command.")
        else:
            self.voice_module.stop_listening()
            self.voice_btn_var.set("🎙 Voice: OFF")
            self.voice_toggle_btn.configure(fg=THEME["text_secondary"])
            self._append_system("🔇 Voice listening deactivated.")
        self.config.save()

    def _toggle_tts(self):
        if not self.voice_module or not self.voice_module.tts_available:
            self._append_system("⚠️ TTS unavailable. Install: pip install pyttsx3")
            return
        self.config.tts_enabled = not self.config.tts_enabled
        if self.config.tts_enabled:
            self.tts_btn_var.set("🔊 TTS: ON")
            self.tts_toggle_btn.configure(fg=THEME["accent"])
            self._append_system("🔊 Text-to-speech enabled.")
        else:
            self.tts_btn_var.set("🔊 TTS: OFF")
            self.tts_toggle_btn.configure(fg=THEME["text_secondary"])
            self._append_system("🔇 Text-to-speech disabled.")
        self.config.save()

    # ─── Settings Dialog ──────────────────────────────────────────────────────

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("JARVIS Settings")
        win.geometry("480x420")
        win.configure(bg=THEME["bg_panel"])
        win.resizable(False, False)

        tk.Label(win, text="⚙ SETTINGS", fg=THEME["accent"],
                 bg=THEME["bg_panel"], font=("Courier", 14, "bold")).pack(pady=15)

        frame = tk.Frame(win, bg=THEME["bg_panel"])
        frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # API Key field
        tk.Label(frame, text="OpenAI API Key:", fg=THEME["text_secondary"],
                 bg=THEME["bg_panel"], font=("Courier", 10)).grid(row=0, column=0, sticky="w", pady=8)
        api_var = tk.StringVar(value=self.config.openai_api_key or "")
        api_entry = tk.Entry(frame, textvariable=api_var, width=35, show="*",
                             bg=THEME["bg_input"], fg=THEME["text_primary"],
                             insertbackground=THEME["accent"],
                             font=("Courier", 10), relief=tk.FLAT)
        api_entry.grid(row=0, column=1, padx=8, pady=8)

        # Model
        tk.Label(frame, text="AI Model:", fg=THEME["text_secondary"],
                 bg=THEME["bg_panel"], font=("Courier", 10)).grid(row=1, column=0, sticky="w", pady=8)
        model_var = tk.StringVar(value=self.config.ai_model)
        model_combo = ttk.Combobox(frame, textvariable=model_var, width=32,
                                   values=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"])
        model_combo.grid(row=1, column=1, padx=8)

        # Wake word
        tk.Label(frame, text="Wake Word:", fg=THEME["text_secondary"],
                 bg=THEME["bg_panel"], font=("Courier", 10)).grid(row=2, column=0, sticky="w", pady=8)
        wake_var = tk.StringVar(value=self.config.wake_word)
        tk.Entry(frame, textvariable=wake_var, width=20,
                 bg=THEME["bg_input"], fg=THEME["text_primary"],
                 insertbackground=THEME["accent"],
                 font=("Courier", 10), relief=tk.FLAT).grid(row=2, column=1, padx=8, sticky="w")

        # Confirm shutdown
        confirm_var = tk.BooleanVar(value=self.config.require_confirmation_for_shutdown)
        tk.Checkbutton(frame, text="Confirm shutdown/restart",
                       variable=confirm_var,
                       bg=THEME["bg_panel"], fg=THEME["text_primary"],
                       selectcolor=THEME["bg_input"],
                       activebackground=THEME["bg_panel"],
                       font=("Courier", 10)).grid(row=3, column=0, columnspan=2, sticky="w", pady=8)

        def _save():
            self.config.openai_api_key = api_var.get().strip()
            self.config.ai_model = model_var.get()
            self.config.wake_word = wake_var.get().strip().lower()
            self.config.require_confirmation_for_shutdown = confirm_var.get()
            self.config.require_confirmation_for_restart = confirm_var.get()
            self.config.save()
            if self.executor:
                self.executor.brain.reload_client()
            self._append_system("✅ Settings saved.")
            win.destroy()

        tk.Button(win, text="💾 SAVE SETTINGS", command=_save,
                  bg=THEME["accent2"], fg="white",
                  activebackground=THEME["accent"],
                  font=("Courier", 11, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  padx=20, pady=8).pack(pady=20)

    # ─── Utilities ────────────────────────────────────────────────────────────

    def _clear_chat(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        self._show_welcome()

    def _on_close(self):
        if messagebox.askokcancel("Exit JARVIS", "Shut down JARVIS?"):
            if self.voice_module:
                self.voice_module.stop_listening()
            self.root.destroy()

    def run(self):
        self.root.mainloop()
