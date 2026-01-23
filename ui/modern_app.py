"""
Modern GUI for the AI Assistant (CustomTkinter)

Provides a clean, modern interface with:
- Text command input
- Push-to-talk voice button
- Optional wake-word toggle
- Live activity log + status bar
"""

from __future__ import annotations

import queue
import time
from dataclasses import replace
from typing import Optional

import customtkinter as ctk

from nlp.intent_parser import Intent
from ui.controller import AssistantController, AssistantSettings


class ModernAssistantUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("AI Assistant")
        self.geometry("980x640")
        self.minsize(900, 600)

        self._ui_queue: "queue.Queue[tuple[str, object]]" = queue.Queue()
        self._settings = AssistantSettings()

        self._controller = AssistantController(
            settings=self._settings,
            on_log=lambda msg: self._ui_queue.put(("log", msg)),
            on_status=lambda msg: self._ui_queue.put(("status", msg)),
            on_intent=lambda intent: self._ui_queue.put(("intent", intent)),
            on_result=lambda res: self._ui_queue.put(("result", res)),
        )

        self._build_layout()
        self._set_status("Stopped")
        self._append_log("system", "Ready. Click Start to initialize the assistant.")

        self.after(60, self._drain_queue)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, corner_radius=12)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=16, pady=16)

        title = ctk.CTkLabel(
            self.sidebar,
            text="Spark Assistant",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: -")
        self.status_label.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        self.wake_status_label = ctk.CTkLabel(self.sidebar, text="Wake word: OFF", text_color="#9aa4b2")
        self.wake_status_label.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="w")

        self.start_btn = ctk.CTkButton(self.sidebar, text="Start", command=self._on_start)
        self.start_btn.grid(row=3, column=0, padx=16, pady=(0, 8), sticky="ew")

        self.stop_btn = ctk.CTkButton(self.sidebar, text="Stop", command=self._on_stop, state="disabled")
        self.stop_btn.grid(row=4, column=0, padx=16, pady=(0, 16), sticky="ew")

        self.tts_var = ctk.BooleanVar(value=self._settings.enable_tts)
        self.wake_var = ctk.BooleanVar(value=self._settings.enable_wake_word)

        self.tts_switch = ctk.CTkSwitch(self.sidebar, text="Voice responses (TTS)", variable=self.tts_var, command=self._on_toggle_settings)
        self.tts_switch.grid(row=5, column=0, padx=16, pady=(0, 8), sticky="w")

        self.wake_switch = ctk.CTkSwitch(self.sidebar, text="Wake word mode", variable=self.wake_var, command=self._on_toggle_settings)
        self.wake_switch.grid(row=6, column=0, padx=16, pady=(0, 16), sticky="w")

        wake_hint = ctk.CTkLabel(self.sidebar, text='Wake words: "hey assistant", "computer"', text_color="#9aa4b2")
        wake_hint.grid(row=7, column=0, padx=16, pady=(0, 8), sticky="w")

        # Main area
        self.main = ctk.CTkFrame(self, corner_radius=12)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.main, corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        self.intent_label = ctk.CTkLabel(header, text="Intent: -", anchor="w")
        self.intent_label.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

        # Chat-style scrollable frame
        self.chat_frame = ctk.CTkScrollableFrame(self.main, corner_radius=12)
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self._chat_rows = 0

        # Input row
        input_row = ctk.CTkFrame(self.main, corner_radius=12)
        input_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        input_row.grid_columnconfigure(0, weight=1)

        self.text_entry = ctk.CTkEntry(input_row, placeholder_text="Type a command (e.g., open chrome, volume up, set timer for 1 minutes)")
        self.text_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.text_entry.bind("<Return>", lambda _e: self._on_send_text())

        self.send_btn = ctk.CTkButton(input_row, text="Send", command=self._on_send_text, width=90)
        self.send_btn.grid(row=0, column=1, padx=(0, 12), pady=12)

        self.voice_btn = ctk.CTkButton(input_row, text="🎤 Speak", command=self._on_speak, width=110)
        self.voice_btn.grid(row=0, column=2, padx=(0, 12), pady=12)

        # Action buttons row
        actions_row = ctk.CTkFrame(self.main, corner_radius=12)
        actions_row.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
        actions_row.grid_columnconfigure(0, weight=1)

        self.clear_btn = ctk.CTkButton(actions_row, text="Clear Log", command=self._clear_chat, width=100)
        self.clear_btn.grid(row=0, column=0, padx=8, pady=8, sticky="w")

    def _append_log(self, role: str, msg: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        bubble = ctk.CTkFrame(self.chat_frame, corner_radius=10)
        bubble.grid(row=self._chat_rows, column=0, sticky="ew", pady=4, padx=6)
        bubble.grid_columnconfigure(0, weight=1)

        header_text = f"{role.capitalize()} · {timestamp}"
        header = ctk.CTkLabel(bubble, text=header_text, text_color="#a0aabe", anchor="w")
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(6, 2))

        bg_color = "#1f2937" if role == "user" else "#111827" if role == "assistant" else "#0f172a"
        text_label = ctk.CTkLabel(
            bubble,
            text=msg,
            fg_color=bg_color,
            corner_radius=8,
            justify="left",
            anchor="w",
            padx=10,
            pady=8,
            wraplength=780,
        )
        text_label.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self._chat_rows += 1
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _set_status(self, status: str) -> None:
        # Special-case wake word status messages to update dedicated label
        if status.startswith("Wake word:"):
            self.wake_status_label.configure(text=status)
        else:
            self.status_label.configure(text=f"Status: {status}")

    def _set_intent(self, intent: Intent) -> None:
        self.intent_label.configure(text=f"Intent: {intent.type.value} (conf: {intent.confidence:.2f})")

    def _on_start(self) -> None:
        # Apply latest switches before start
        self._apply_settings()
        ok = self._controller.start()
        if ok:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self._append_log("system", "Failed to start. Check your microphone and dependencies.")

    def _on_stop(self) -> None:
        self._controller.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._set_status("Stopped")

    def _on_toggle_settings(self) -> None:
        # If running, allow wake-word toggle live; other settings apply on restart
        if self._controller.is_running:
            self._controller.set_wake_word_enabled(bool(self.wake_var.get()))
        self._apply_settings()

    def _apply_settings(self) -> None:
        self._settings = replace(
            self._settings,
            enable_tts=bool(self.tts_var.get()),
            enable_wake_word=bool(self.wake_var.get()),
        )
        # Recreate controller only when not running
        if not self._controller.is_running:
            self._controller = AssistantController(
                settings=self._settings,
                on_log=lambda msg: self._ui_queue.put(("log", msg)),
                on_status=lambda msg: self._ui_queue.put(("status", msg)),
                on_intent=lambda intent: self._ui_queue.put(("intent", intent)),
                on_result=lambda res: self._ui_queue.put(("result", res)),
            )

    def _on_send_text(self) -> None:
        text = self.text_entry.get().strip()
        if not text:
            return
        if not self._controller.is_running:
            self._append_log("system", "Start the assistant first.")
            return
        self.text_entry.delete(0, "end")
        self._append_log("user", text)
        self._controller.run_text_command(text)

    def _on_speak(self) -> None:
        if not self._controller.is_running:
            self._append_log("system", "Start the assistant first.")
            return
        self._append_log("system", "Listening for voice input...")
        self._controller.run_voice_command()

    def _clear_chat(self) -> None:
        for child in self.chat_frame.winfo_children():
            child.destroy()
        self._chat_rows = 0

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self._ui_queue.get_nowait()
                if kind == "log":
                    self._append_log("assistant", str(payload))
                elif kind == "status":
                    self._set_status(str(payload))
                elif kind == "intent" and isinstance(payload, Intent):
                    self._set_intent(payload)
                elif kind == "result" and isinstance(payload, dict):
                    msg = payload.get("message", "")
                    self._append_log("assistant", msg)
        except queue.Empty:
            pass
        self.after(60, self._drain_queue)


def main() -> None:
    app = ModernAssistantUI()
    app.mainloop()


if __name__ == "__main__":
    main()

