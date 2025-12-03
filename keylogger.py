#!/usr/bin/env python3
"""
typing_recorder.py

A safe, local Tkinter app that records keystrokes only while the app window is focused.
Intended for legitimate uses (typing practice, debugging input handling, accessibility testing).
This does NOT capture global/system-wide keystrokes.

Requires Python 3 (Tkinter included in most standard installs).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class TypingRecorder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Typing Recorder (safe demo)")
        self.geometry("720x480")
        self.minsize(600, 400)

        self.recording = False
        self.log = []  # list of tuples: (timestamp_str, event_keysym, char)

        self._build_ui()

    def _build_ui(self):
        # Top controls
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill="x", padx=12, pady=8)

        self.start_btn = ttk.Button(ctrl_frame, text="Start Recording", command=self.start_recording)
        self.start_btn.pack(side="left", padx=(0,6))

        self.stop_btn = ttk.Button(ctrl_frame, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.stop_btn.pack(side="left", padx=(0,6))

        self.save_btn = ttk.Button(ctrl_frame, text="Save Log...", command=self.save_log)
        self.save_btn.pack(side="left", padx=(8,6))

        clear_btn = ttk.Button(ctrl_frame, text="Clear Log", command=self.clear_log)
        clear_btn.pack(side="left")

        # Info label
        self.info_label = ttk.Label(ctrl_frame, text="Status: Idle — the app records only while focused and recording.")
        self.info_label.pack(side="right")

        # Middle: a text box to focus and type into
        middle_frame = ttk.Frame(self)
        middle_frame.pack(fill="both", expand=True, padx=12, pady=(0,12))

        left_pane = ttk.Frame(middle_frame)
        left_pane.pack(side="left", fill="both", expand=True)

        ttk.Label(left_pane, text="Type here (this area receives keyboard events):").pack(anchor="w")
        self.type_area = tk.Text(left_pane, wrap="word", height=10)
        self.type_area.pack(fill="both", expand=True, pady=(4,0))

        # Right pane: recorded events
        right_pane = ttk.Frame(middle_frame, width=320)
        right_pane.pack(side="right", fill="y")

        ttk.Label(right_pane, text="Recorded events").pack(anchor="w")
        self.tree = ttk.Treeview(right_pane, columns=("time","key","char"), show="headings", height=18)
        self.tree.heading("time", text="Time")
        self.tree.heading("key", text="Keysym")
        self.tree.heading("char", text="Char")
        self.tree.column("time", width=130, anchor="w")
        self.tree.column("key", width=100, anchor="w")
        self.tree.column("char", width=60, anchor="w")
        self.tree.pack(fill="y", expand=True, pady=(4,0))

        # Bind focus in/out to inform user that recording requires focus
        self.bind("<FocusIn>", lambda e: self._update_status())
        self.bind("<FocusOut>", lambda e: self._update_status())

        # Bind window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_recording(self):
        if self.recording:
            return
        # Bind key events to the type_area widget (only when focused)
        self.type_area.bind("<Key>", self._on_key)
        self.recording = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._update_status()
        self.type_area.focus_set()

    def stop_recording(self):
        if not self.recording:
            return
        self.type_area.unbind("<Key>")
        self.recording = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._update_status()

    def _on_key(self, event):
        # Records the event: keysym (key identifier) and the actual char (if printable)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        keysym = event.keysym  # e.g., "a", "Return", "BackSpace"
        char = event.char if event.char and event.char.isprintable() else ""
        self.log.append((ts, keysym, char))
        # Insert into treeview
        self.tree.insert("", "end", values=(ts, keysym, char))
        # allow normal text insertion in the Text widget
        # return None -> default behavior continues

    def save_log(self):
        if not self.log:
            messagebox.showinfo("Save Log", "No events to save.")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files","*.txt"), ("All files","*.*")],
                                             title="Save recorded keystrokes")
        if not fpath:
            return
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("# Typing Recorder Log\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write("# Columns: timestamp | keysym | char (char empty if non-printable)\n\n")
                for ts, keysym, char in self.log:
                    # sanitize char for printing
                    safe_char = char if char else ""
                    f.write(f"{ts}\t{keysym}\t{safe_char}\n")
            messagebox.showinfo("Save Log", f"Saved {len(self.log)} events to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Save Log", f"Failed to save file:\n{e}")

    def clear_log(self):
        if not self.log:
            return
        if not messagebox.askyesno("Clear Log", "Clear recorded events from the app?"):
            return
        self.log.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _update_status(self):
        focused = self.focus_displayof() is not None
        if self.recording:
            if focused:
                status = "Recording (window focused)"
            else:
                status = "Recording (window not focused) — keystrokes only recorded when focused"
        else:
            status = "Idle — press Start Recording"
        self.info_label.config(text=f"Status: {status}")

    def on_close(self):
        if self.recording:
            if not messagebox.askyesno("Quit", "Recording is in progress. Stop and quit?"):
                return
        self.destroy()

if __name__ == "__main__":
    app = TypingRecorder()
    app.mainloop()
