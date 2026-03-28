import customtkinter as ctk
from tkinter import filedialog
import threading
from webdriver_setup import setup_webdriver
from playlist_scraper import get_playlist_info
from youtube_downloader import download_video, download_audio

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

C = {
    "bg":          "#0f0f0f",
    "surface":     "#1a1a1a",
    "elevated":    "#1f1f1f",
    "input":       "#1a1a1a",
    "border":      "#272727",
    "border2":     "#333333",
    "red":         "#ff0000",
    "red_hover":   "#cc0000",
    "white":       "#ffffff",
    "gray1":       "#f1f1f1",
    "gray2":       "#aaaaaa",
    "gray3":       "#717171",
    "gray4":       "#4d4d4d",
    "gray5":       "#272727",
    "green_bg":    "#0d2a0d",
    "green_fg":    "#2ea82e",
    "green_bg2":   "#1a2a1a",
    "green_fg2":   "#4caf50",
    "error_bg":    "#2a0d0d",
    "error_fg":    "#e05252",
}

# ================================================
# Track Row Widget
# ================================================

class TrackRow(ctk.CTkFrame):
    """Single track row with index, title, and live status pill."""

    def __init__(self, parent, index, title, **kwargs):
        super().__init__(parent, fg_color="transparent", height=40, **kwargs)
        self.pack_propagate(False)

        # Index
        self.index_lbl = ctk.CTkLabel(
            self,
            text=f"{index:>2}",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=C["gray4"],
            width=28,
            anchor="e"
        )
        self.index_lbl.pack(side="left", padx=(12, 8))

        # Title
        self.title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Roboto", size=14),
            text_color=C["gray1"],
            anchor="w"
        )
        self.title_lbl.pack(side="left", fill="x", expand=True)

        # Status pill
        self.pill = ctk.CTkLabel(
            self,
            text="  Waiting  ",
            font=ctk.CTkFont(family="Roboto", size=11, weight="bold"),
            text_color=C["gray4"],
            fg_color=C["gray5"],
            corner_radius=10,
            width=90
        )
        self.pill.pack(side="right", padx=12)

    def set_downloading(self):
        self.configure(fg_color=C["elevated"])
        self.index_lbl.configure(text="▶", text_color=C["red"])
        self.title_lbl.configure(text_color=C["white"])
        self.pill.configure(text="  Downloading  ", text_color=C["green_fg2"], fg_color=C["green_bg2"])

    def set_done(self):
        self.configure(fg_color="transparent")
        self.index_lbl.configure(text_color=C["gray4"])
        self.title_lbl.configure(text_color=C["gray2"])
        self.pill.configure(text="  Done  ", text_color=C["green_fg"], fg_color=C["green_bg"])

    def set_error(self):
        self.configure(fg_color="transparent")
        self.pill.configure(text="  Error  ", text_color=C["error_fg"], fg_color=C["error_bg"])

    def reset(self):
        self.configure(fg_color="transparent")
        self.index_lbl.configure(text_color=C["gray4"])
        self.title_lbl.configure(text_color=C["gray1"])
        self.pill.configure(text="  Waiting  ", text_color=C["gray4"], fg_color=C["gray5"])


# ================================================
# Main App
# ================================================

class YoutubeDownloaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Playlist Downloader")
        self.geometry("640x820")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])

        # Round window corners (Windows 11)
        try:
            from ctypes import windll, byref, sizeof, c_int
            HWND = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(HWND, 33, byref(c_int(2)), sizeof(c_int))
        except Exception:
            pass

        self.videos     = []
        self.save_path  = ""
        self.track_rows = []

        self._build_ui()

    # ─────────────────────────────────────────────
    # UI Builder
    # ─────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_url_input()
        self._build_folder_input()
        self._build_fetch_button()
        self._build_playlist_card()
        self._build_tracklist()
        self._build_download_buttons()
        self._build_status_bar()

    def _build_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=(28, 24))

        # YouTube red icon
        icon = ctk.CTkFrame(f, width=48, height=34, corner_radius=7, fg_color=C["red"])
        icon.pack(side="left", padx=(0, 12))
        icon.pack_propagate(False)
        ctk.CTkLabel(
            icon, text="▶",
            font=ctk.CTkFont(size=18),
            text_color=C["white"]
        ).place(relx=0.55, rely=0.5, anchor="center")

        text = ctk.CTkFrame(f, fg_color="transparent")
        text.pack(side="left")
        ctk.CTkLabel(
            text, text="Playlist Downloader",
            font=ctk.CTkFont(family="Roboto", size=24, weight="bold"),
            text_color=C["white"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            text, text="Save YouTube playlists as MP4 or MP3",
            font=ctk.CTkFont(family="Roboto", size=13),
            text_color=C["gray3"]
        ).pack(anchor="w")

    def _build_url_input(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkLabel(
            f, text="PLAYLIST URL",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=C["gray1"]
        ).pack(anchor="w", pady=(0, 8))

        self.url_entry = ctk.CTkEntry(
            f,
            placeholder_text="https://www.youtube.com/playlist?list=...",
            height=46,
            corner_radius=8,
            border_width=1,
            border_color=C["border"],
            fg_color=C["input"],
            text_color=C["white"],
            placeholder_text_color=C["gray4"],
            font=ctk.CTkFont(family="Roboto", size=13)
        )
        self.url_entry.pack(fill="x")

    def _build_folder_input(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkLabel(
            f, text="SAVE TO",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=C["gray1"]
        ).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")

        self.folder_entry = ctk.CTkEntry(
            row,
            placeholder_text="Choose a folder...",
            height=46,
            corner_radius=8,
            border_width=1,
            border_color=C["border"],
            fg_color=C["input"],
            text_color=C["white"],
            placeholder_text_color=C["gray4"],
            font=ctk.CTkFont(family="Roboto", size=13),
            state="disabled"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row,
            text="Browse",
            width=90,
            height=46,
            corner_radius=8,
            fg_color=C["gray5"],
            hover_color=C["border2"],
            text_color=C["gray2"],
            border_width=1,
            border_color=C["border2"],
            font=ctk.CTkFont(family="Roboto", size=13, weight="bold"),
            command=self._browse_folder
        ).pack(side="right")

    def _build_fetch_button(self):
        self.fetch_btn = ctk.CTkButton(
            self,
            text="Fetch Playlist",
            height=50,
            corner_radius=10,
            fg_color=C["gray5"],
            hover_color=C["gray4"],
            text_color=C["white"],
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            command=self._fetch_playlist
        )
        self.fetch_btn.pack(fill="x", padx=28, pady=(0, 22))

    def _build_playlist_card(self):
        card = ctk.CTkFrame(
            self,
            fg_color=C["surface"],
            corner_radius=12,
            border_width=1,
            border_color=C["border"]
        )
        card.pack(fill="x", padx=28, pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Thumbnail placeholder
        thumb = ctk.CTkFrame(inner, width=48, height=48, corner_radius=8, fg_color=C["gray5"])
        thumb.pack(side="left", padx=(0, 14))
        thumb.pack_propagate(False)
        ctk.CTkLabel(
            thumb, text="▶",
            font=ctk.CTkFont(size=16),
            text_color=C["gray4"]
        ).place(relx=0.55, rely=0.5, anchor="center")

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        self.playlist_name_lbl = ctk.CTkLabel(
            info, text="No playlist loaded",
            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
            text_color=C["gray3"],
            anchor="w"
        )
        self.playlist_name_lbl.pack(anchor="w")

        self.creator_lbl = ctk.CTkLabel(
            info, text="",
            font=ctk.CTkFont(family="Roboto", size=12),
            text_color=C["gray4"],
            anchor="w"
        )
        self.creator_lbl.pack(anchor="w", pady=(3, 0))

        self.count_badge = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(family="Roboto", size=12, weight="bold"),
            text_color=C["gray2"],
            fg_color=C["gray5"],
            corner_radius=20,
            padx=12,
            pady=4
        )
        self.count_badge.pack(side="right")

    def _build_tracklist(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=(0, 16))

        ctk.CTkLabel(
            f, text="TRACKS",
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=C["gray1"]
        ).pack(anchor="w", pady=(0, 8))

        card = ctk.CTkFrame(
            f,
            fg_color=C["surface"],
            corner_radius=12,
            border_width=1,
            border_color=C["border"]
        )
        card.pack(fill="x")

        self.tracklist_scroll = ctk.CTkScrollableFrame(
            card,
            height=200,
            fg_color="transparent",
            scrollbar_button_color=C["border"],
            scrollbar_button_hover_color=C["gray4"]
        )
        self.tracklist_scroll.pack(fill="x", padx=0, pady=4)

        self.empty_label = ctk.CTkLabel(
            self.tracklist_scroll,
            text="Fetch a playlist to see tracks here",
            font=ctk.CTkFont(family="Roboto", size=13),
            text_color=C["gray4"]
        )
        self.empty_label.pack(pady=40)

    def _build_download_buttons(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=28, pady=(0, 14))

        self.download_mp4_btn = ctk.CTkButton(
            f,
            text="⬇  Download MP4",
            height=50,
            corner_radius=10,
            fg_color=C["gray5"],
            hover_color=C["border2"],
            text_color=C["white"],
            border_width=1,
            border_color=C["border2"],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            state="disabled",
            command=lambda: self._start_download("v")
        )
        self.download_mp4_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.download_mp3_btn = ctk.CTkButton(
            f,
            text="♪  Download MP3",
            height=50,
            corner_radius=10,
            fg_color=C["red"],
            hover_color=C["red_hover"],
            text_color=C["white"],
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            state="disabled",
            command=lambda: self._start_download("a")
        )
        self.download_mp3_btn.pack(side="right", expand=True, fill="x", padx=(8, 0))

    def _build_status_bar(self):
        card = ctk.CTkFrame(
            self,
            fg_color=C["surface"],
            corner_radius=12,
            border_width=1,
            border_color=C["border"]
        )
        card.pack(fill="x", padx=28, pady=(0, 28))
        self.status_card = card

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 10))

        self.status_label = ctk.CTkLabel(
            top, text="Ready",
            font=ctk.CTkFont(family="Roboto", size=13),
            text_color=C["gray3"],
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self.progress_count = ctk.CTkLabel(
            top, text="",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=C["gray3"]
        )
        self.progress_count.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(
            card,
            height=3,
            corner_radius=2,
            fg_color=C["gray5"],
            progress_color=C["red"],
            border_width=0
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 14))
        self.progress_bar.set(0)

    # ─────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path = folder
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="disabled")

    def _fetch_playlist(self):
        url = self.url_entry.get().strip()
        if not url:
            self._set_status("Please enter a playlist URL", "error")
            return
        if not self.save_path:
            self._set_status("Please select a save folder", "error")
            return
        self._set_status("Fetching playlist...", "muted")
        self.fetch_btn.configure(state="disabled", text="Fetching...")
        threading.Thread(target=self._fetch_worker, args=(url,), daemon=True).start()

    def _fetch_worker(self, url):
        try:
            driver = setup_webdriver()
            playlist_name, creator_name, videos = get_playlist_info(driver, url)
            driver.quit()
            self.videos = videos
            self.after(0, lambda: self._on_fetch_complete(playlist_name, creator_name, videos))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"Error: {e}", "error"))
            self.after(0, lambda: self.fetch_btn.configure(state="normal", text="Fetch Playlist"))

    def _on_fetch_complete(self, playlist_name, creator_name, videos):
        self.playlist_name_lbl.configure(text=playlist_name, text_color=C["white"])
        self.creator_lbl.configure(text=f"by {creator_name}", text_color=C["gray3"])
        self.count_badge.configure(text=f"  {len(videos)} tracks  ")

        for w in self.tracklist_scroll.winfo_children():
            w.destroy()
        self.track_rows = []

        for i, video in enumerate(videos, start=1):
            row = TrackRow(self.tracklist_scroll, i, video["title"])
            row.pack(fill="x")
            if i < len(videos):
                ctk.CTkFrame(
                    self.tracklist_scroll,
                    height=1,
                    fg_color=C["elevated"]
                ).pack(fill="x", padx=12)
            self.track_rows.append(row)

        self.download_mp4_btn.configure(state="normal")
        self.download_mp3_btn.configure(state="normal")
        self.fetch_btn.configure(state="normal", text="Fetch Playlist")
        self._set_status(f"Ready — {len(videos)} tracks loaded", "success")
        self.progress_bar.set(0)
        self.progress_count.configure(text="")

    def _start_download(self, choice):
        if not self.videos:
            return
        for row in self.track_rows:
            row.reset()
        self.download_mp4_btn.configure(state="disabled")
        self.download_mp3_btn.configure(state="disabled")
        self.fetch_btn.configure(state="disabled")
        self.progress_bar.set(0)
        threading.Thread(target=self._download_worker, args=(choice,), daemon=True).start()

    def _download_worker(self, choice):
        total = len(self.videos)
        for index, (video, row) in enumerate(zip(self.videos, self.track_rows), start=1):
            self.after(0, row.set_downloading)
            self.after(0, lambda i=index, t=total, title=video["title"]: (
                self._set_status(f"Downloading: {title}", "muted"),
                self.progress_count.configure(text=f"{i} / {t}"),
                self.progress_bar.set((i - 1) / t)
            ))
            try:
                if choice == "v":
                    download_video(video["url"], self.save_path)
                else:
                    download_audio(video["url"], self.save_path)
                self.after(0, row.set_done)
            except Exception:
                self.after(0, row.set_error)

            self.after(0, lambda i=index, t=total: (
                self.progress_bar.set(i / t),
                self.progress_count.configure(text=f"{i} / {t}")
            ))

        self.after(0, self._on_download_complete)

    def _on_download_complete(self):
        total = len(self.videos)
        self.progress_bar.set(1)
        self.progress_count.configure(text=f"{total} / {total}")
        self._set_status(f"All {total} tracks downloaded successfully ✓", "success")
        self.download_mp4_btn.configure(state="normal")
        self.download_mp3_btn.configure(state="normal")
        self.fetch_btn.configure(state="normal")
        self.status_card.configure(border_color=C["red"])
        self.after(2000, lambda: self.status_card.configure(border_color=C["border"]))

    def _set_status(self, message, level="muted"):
        colors = {
            "muted":   C["gray3"],
            "success": C["green_fg"],
            "error":   C["error_fg"],
        }
        self.status_label.configure(
            text=message,
            text_color=colors.get(level, C["gray3"])
        )


# ================================================
# Entry Point
# ================================================

if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()