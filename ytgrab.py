import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import sys
import os

__version__ = "1.0.0"


def _ensure_deps():
    required = {"yt-dlp": "yt_dlp", "imageio-ffmpeg": "imageio_ffmpeg"}
    for pkg, mod in required.items():
        try:
            __import__(mod)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


_ensure_deps()

import yt_dlp
import imageio_ffmpeg

DARK_BG = "#1a1a2e"
PANEL_BG = "#16213e"
ACCENT  = "#e94560"
FG      = "#ffffff"
MUTED   = "#a8dadc"


class YTGrab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"ytgrab  v{__version__}")
        self.resizable(False, False)
        self.configure(bg=DARK_BG)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="YouTube Downloader", font=("Segoe UI", 14, "bold"),
                 bg=DARK_BG, fg=ACCENT).pack(padx=18, pady=(16, 2))
        tk.Label(self, text="Highest quality · MP4", font=("Segoe UI", 9),
                 bg=DARK_BG, fg=MUTED).pack(padx=18, pady=(0, 10))

        tk.Label(self, text="URL", font=("Segoe UI", 10, "bold"),
                 bg=DARK_BG, fg=FG).pack(anchor="w", padx=18)
        self.url_var = tk.StringVar()
        url_frame = tk.Frame(self, bg=PANEL_BG, pady=4, padx=6)
        url_frame.pack(fill="x", padx=18, pady=(2, 10))
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=52,
                                  font=("Segoe UI", 10), bg=PANEL_BG, fg=FG,
                                  insertbackground=FG, relief="flat", bd=0)
        self.url_entry.pack(fill="x")
        self.url_entry.bind("<Control-a>",
                            lambda e: (self.url_entry.select_range(0, "end"), "break")[1])

        tk.Label(self, text="Save to", font=("Segoe UI", 10, "bold"),
                 bg=DARK_BG, fg=FG).pack(anchor="w", padx=18)
        self.dir_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        dir_frame = tk.Frame(self, bg=DARK_BG)
        dir_frame.pack(fill="x", padx=18, pady=(2, 14))
        tk.Label(dir_frame, textvariable=self.dir_var, bg=PANEL_BG, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w", padx=6, pady=4, width=44).pack(side="left")
        tk.Button(dir_frame, text="Browse", command=self._browse,
                  bg=ACCENT, fg=FG, font=("Segoe UI", 9), relief="flat",
                  padx=10, cursor="hand2", activebackground="#c73652").pack(side="left", padx=(6, 0))

        self.dl_btn = tk.Button(self, text="Download", command=self._start,
                                bg=ACCENT, fg=FG, font=("Segoe UI", 12, "bold"),
                                relief="flat", padx=22, pady=8, cursor="hand2",
                                activebackground="#c73652")
        self.dl_btn.pack(pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready — paste a URL and press Download.")
        self.status_lbl = tk.Label(self, textvariable=self.status_var, bg=DARK_BG, fg=MUTED,
                                   font=("Segoe UI", 9), wraplength=440, justify="left")
        self.status_lbl.pack(padx=18, pady=(0, 16))

    def _browse(self):
        path = filedialog.askdirectory(initialdir=self.dir_var.get())
        if path:
            self.dir_var.set(path)

    def _start(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Paste a YouTube URL to continue.")
            return
        self.dl_btn.config(state="disabled")
        self._set_status("Starting…", MUTED)
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(self.dir_var.get(), "%(title)s.%(ext)s"),
            "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
            "progress_hooks": [self._progress],
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_done)
        except Exception as exc:
            self.after(0, lambda e=str(exc): self._on_error(e))

    def _progress(self, d):
        if d.get("status") == "downloading":
            pct   = d.get("_percent_str", "?%").strip()
            speed = d.get("_speed_str", "?").strip()
            eta   = d.get("_eta_str", "?").strip()
            msg   = f"Downloading  {pct}   {speed}   ETA {eta}"
            self.after(0, lambda m=msg: self._set_status(m, MUTED))
        elif d.get("status") == "finished":
            self.after(0, lambda: self._set_status("Merging streams…", MUTED))

    def _on_done(self):
        self._set_status("Done!  Saved to: " + self.dir_var.get(), "#4caf50")
        self.dl_btn.config(state="normal")

    def _on_error(self, msg):
        self._set_status("Error: " + (msg.splitlines()[-1] if msg else "unknown"), "#ef5350")
        self.dl_btn.config(state="normal")

    def _set_status(self, text, color=MUTED):
        self.status_var.set(text)
        self.status_lbl.config(fg=color)


if __name__ == "__main__":
    YTGrab().mainloop()
