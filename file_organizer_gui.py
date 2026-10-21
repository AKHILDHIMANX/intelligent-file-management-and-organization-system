"""
Mini File Organizer - Tkinter GUI Version
-----------------------------------------
Organizes files in a folder into subfolders based on their extension.
Includes a Restore (Undo) feature that puts files back to their
original location.

MCA Mini Project
Modules used: tkinter, pathlib, shutil, json
"""

import json
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox, ttk

# ---------------- Category mapping ----------------
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".java", ".c", ".cpp", ".html", ".css", ".js"],
    "Others": [],
}

SCRIPT_NAME = "file_organizer_gui.py"
LOG_NAME = ".organizer_history.json"   # hidden history file (for Undo)

# ---------------- Theme colors ----------------
C_HEADER = "#1f2a38"
C_BODY = "#f4f6f8"
C_WHITE = "#ffffff"
C_BORDER = "#dfe6e9"
C_BLUE = "#3498db"
C_ORANGE = "#f39c12"
C_GREEN = "#27ae60"
C_PURPLE = "#8e44ad"
C_GREY = "#7f8c8d"
C_MUTED = "#636e72"
ROW_EVEN = "#ffffff"
ROW_ODD = "#f8fafc"


# ---------------- Helper functions ----------------
def get_category(suffix: str) -> str:
    """Return the folder name for a given file extension."""
    suffix = suffix.lower()
    for folder, extensions in CATEGORIES.items():
        if suffix in extensions:
            return folder
    return "Others"


def unique_path(dest: Path) -> Path:
    """Return a non-existing path by adding _1, _2 ... if required."""
    if not dest.exists():
        return dest
    n = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}_{n}{dest.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def load_history(folder: Path) -> list:
    """Read the saved move-history of a folder."""
    log = folder / LOG_NAME
    if log.is_file():
        try:
            return json.loads(log.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history(folder: Path, moves: list) -> None:
    """Append moves to the hidden history file (used by Undo)."""
    log = folder / LOG_NAME
    log.write_text(json.dumps(load_history(folder) + moves, indent=2))


def clear_history(folder: Path) -> None:
    log = folder / LOG_NAME
    if log.exists():
        log.unlink()


# ---------------- GUI ----------------
class FileOrganizerApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Mini File Organizer")
        self.root.geometry("780x580")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BODY)

        self.setup_styles()
        self.build_ui()

        self.path_var.trace_add("write", self.check_history)
        self.check_history()

    # ---------------- Styling (colors now visible on macOS) ----------------
    def setup_styles(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")   # clam theme supports custom button colors

        s.configure("Header.TFrame", background=C_HEADER)
        s.configure("Body.TFrame", background=C_BODY)

        s.configure("Title.TLabel", background=C_HEADER, foreground="white",
                    font=("Helvetica", 20, "bold"))
        s.configure("Sub.TLabel", background=C_HEADER, foreground="#a4b0be",
                    font=("Helvetica", 10))

        button_colors = {
            "Blue.TButton":   (C_BLUE, "#2f81b7"),
            "Orange.TButton": (C_ORANGE, "#d68910"),
            "Green.TButton":  (C_GREEN, "#1e8449"),
            "Purple.TButton": (C_PURPLE, "#732b95"),
            "Grey.TButton":   (C_GREY, "#616a6b"),
        }
        for name, (bg, active) in button_colors.items():
            s.configure(name, background=bg, foreground="white",
                        font=("Helvetica", 11, "bold"),
                        padding=(14, 9), borderwidth=0, focuscolor=bg)
            s.map(name,
                  background=[("active", active), ("pressed", active)],
                  foreground=[("disabled", "#ecf0f1")])

        s.configure("Treeview", background=C_WHITE, fieldbackground=C_WHITE,
                    foreground=C_MUTED, rowheight=28,
                    font=("Helvetica", 10), borderwidth=0)
        s.configure("Treeview.Heading", background=C_HEADER, foreground="white",
                    font=("Helvetica", 10, "bold"), relief=FLAT, padding=(8, 7))
        s.map("Treeview",
              background=[("selected", C_BLUE)],
              foreground=[("selected", "white")])
        s.map("Treeview.Heading", background=[("active", "#2c3e50")])

        s.configure("Vertical.TScrollbar", background=C_BORDER,
                    troughcolor=C_BODY, borderwidth=0, arrowsize=14)

    # ---------------- UI layout ----------------
    def build_ui(self):
        # --- Header ---
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(18, 14))
        header.pack(fill=X)
        ttk.Label(header, text="MINI FILE ORGANIZER", style="Title.TLabel").pack(anchor=W)
        ttk.Label(header, text="Sort your folder by file type  |  MCA Mini Project",
                  style="Sub.TLabel").pack(anchor=W)

        # --- Body ---
        body = ttk.Frame(self.root, style="Body.TFrame", padding=(16, 14))
        body.pack(fill=BOTH, expand=True)

        # Card 1 : folder path
        card1 = tk.Frame(body, bg=C_WHITE, highlightbackground=C_BORDER,
                         highlightthickness=1)
        card1.pack(fill=X, pady=(0, 12))
        inner1 = tk.Frame(card1, bg=C_WHITE, padx=14, pady=12)
        inner1.pack(fill=X)

        tk.Label(inner1, text="FOLDER PATH", bg=C_WHITE, fg=C_MUTED,
                 font=("Helvetica", 9, "bold")).pack(anchor=W)

        row = tk.Frame(inner1, bg=C_WHITE)
        row.pack(fill=X, pady=(6, 0))

        self.path_var = StringVar()
        tk.Entry(row, textvariable=self.path_var, bg=C_WHITE, fg="#2d3436",
                 font=("Helvetica", 11), relief=FLAT, highlightthickness=1,
                 highlightbackground=C_BORDER, highlightcolor=C_BLUE
                 ).pack(side=LEFT, fill=X, expand=True, ipady=5)

        ttk.Button(row, text="Browse...", style="Blue.TButton",
                   command=self.browse).pack(side=LEFT, padx=(10, 0))

        self.hint_lbl = tk.Label(inner1, text="", bg=C_WHITE,
                                 font=("Helvetica", 9), anchor=W)
        self.hint_lbl.pack(fill=X, pady=(8, 0))

        # Card 2 : action buttons
        card2 = tk.Frame(body, bg=C_WHITE, highlightbackground=C_BORDER,
                         highlightthickness=1)
        card2.pack(fill=X, pady=(0, 12))
        btn_row = tk.Frame(card2, bg=C_WHITE, padx=14, pady=12)
        btn_row.pack(fill=X)

        actions = [
            ("Preview (Dry Run)", "Orange.TButton", self.preview),
            ("Organize Files", "Green.TButton", self.organize),
            ("Restore / Undo", "Purple.TButton", self.restore),
            ("Clear", "Grey.TButton", self.clear_log),
        ]
        for text, style, cmd in actions:
            ttk.Button(btn_row, text=text, style=style, command=cmd).pack(
                side=LEFT, padx=(0, 10))

        # Card 3 : result table
        card3 = tk.Frame(body, bg=C_WHITE, highlightbackground=C_BORDER,
                         highlightthickness=1)
        card3.pack(fill=BOTH, expand=True)
        inner3 = tk.Frame(card3, bg=C_WHITE, padx=14, pady=12)
        inner3.pack(fill=BOTH, expand=True)

        top3 = tk.Frame(inner3, bg=C_WHITE)
        top3.pack(fill=X)
        tk.Label(top3, text="RESULT", bg=C_WHITE, fg=C_MUTED,
                 font=("Helvetica", 9, "bold")).pack(side=LEFT)
        self.count_var = StringVar(value="")
        tk.Label(top3, textvariable=self.count_var, bg=C_WHITE, fg=C_BLUE,
                 font=("Helvetica", 9, "bold")).pack(side=RIGHT)

        table_frame = tk.Frame(inner3, bg=C_WHITE)
        table_frame.pack(fill=BOTH, expand=True, pady=(6, 0))

        self.tree = ttk.Treeview(
            table_frame, columns=("file", "src", "dst"), show="headings", height=8
        )
        self.tree.heading("file", text="File Name")
        self.tree.heading("src", text="From")
        self.tree.heading("dst", text="To")
        self.tree.column("file", width=310, anchor=W)
        self.tree.column("src", width=180, anchor=W)
        self.tree.column("dst", width=180, anchor=W)

        scroll = ttk.Scrollbar(table_frame, orient=VERTICAL,
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)

        self.tree.tag_configure("even", background=ROW_EVEN)
        self.tree.tag_configure("odd", background=ROW_ODD)

        # --- Status bar ---
        self.status_lbl = tk.Label(
            self.root, text="Ready. Select a folder to begin.",
            anchor=W, bg=C_HEADER, fg="#ecf0f1",
            font=("Helvetica", 10), padx=14, pady=7
        )
        self.status_lbl.pack(fill=X, side=BOTTOM)

    # ---------------- Small helpers ----------------
    def set_status(self, text, color="#ecf0f1"):
        self.status_lbl.config(text=text, fg=color)

    def set_hint(self, text, color=C_MUTED):
        self.hint_lbl.config(text=text, fg=color)

    def add_row(self, name, src, dst):
        count = len(self.tree.get_children())
        tag = "even" if count % 2 == 0 else "odd"
        self.tree.insert("", END, values=(name, src, dst), tags=(tag,))
        self.count_var.set(f"{count + 1} row(s)")

    def clear_log(self):
        self.tree.delete(*self.tree.get_children())
        self.count_var.set("")
        self.set_status("Log cleared.")

    def browse(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.path_var.set(folder)
            self.clear_log()
            self.set_status("Folder selected. Use Preview or Organize.")

    def get_folder(self):
        """Validate the path typed/selected by the user."""
        path = self.path_var.get().strip().strip('"')
        if not path:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return None
        folder = Path(path)
        if not folder.is_dir():
            messagebox.showerror("Error", "Folder not found:\n" + path)
            return None
        return folder

    def get_files(self, folder: Path):
        return [f for f in sorted(folder.iterdir())
                if f.is_file() and f.name not in (SCRIPT_NAME, LOG_NAME)]

    # ---------------- Restore availability hint ----------------
    def check_history(self, *_):
        path = self.path_var.get().strip().strip('"')
        if not path:
            self.set_hint("")
            return
        folder = Path(path)
        if not folder.is_dir():
            self.set_hint("Folder not found", "#e74c3c")
            return

        history = load_history(folder)
        if history:
            self.set_hint(f"Restore available - {len(history)} file(s) recorded in history",
                          C_GREEN)
        elif any((folder / c).is_dir() for c in CATEGORIES):
            self.set_hint("Organized folders detected - Restore will move files back to this folder",
                          C_ORANGE)
        else:
            self.set_hint("No restore history for this folder yet", C_MUTED)

    # ---------------- Actions ----------------
    def preview(self):
        folder = self.get_folder()
        if folder is None:
            return
        files = self.get_files(folder)
        if not files:
            messagebox.showinfo("Info", "No files found in this folder.")
            return

        self.clear_log()
        for f in files:
            self.add_row(f.name, "this folder", get_category(f.suffix) + "/")
        self.set_status(f"Preview: {len(files)} file(s) will be organized. Nothing moved yet.",
                        C_ORANGE)

    def organize(self):
        folder = self.get_folder()
        if folder is None:
            return
        files = self.get_files(folder)
        if not files:
            messagebox.showinfo("Info", "No files found in this folder.")
            return
        if not messagebox.askyesno(
            "Confirm", f"Move {len(files)} file(s) into category folders?\n\n"
                       "You can undo this later with the Restore button."
        ):
            return

        self.clear_log()
        moves = []
        moved = 0

        for item in files:
            category = get_category(item.suffix)
            dest_dir = folder / category
            dest_dir.mkdir(exist_ok=True)
            dest = unique_path(dest_dir / item.name)

            shutil.move(str(item), str(dest))
            moves.append({"original": str(item), "moved_to": str(dest)})
            self.add_row(item.name, "this folder", category + "/")
            moved += 1
            self.set_status(f"Moving... {moved}/{len(files)}", C_BLUE)
            self.root.update_idletasks()

        save_history(folder, moves)          # saved for Undo
        self.check_history()
        self.set_status(f"Done! {moved} file(s) organized. Use Restore to undo.",
                        C_GREEN)
        messagebox.showinfo(
            "Success",
            f"{moved} file(s) organized successfully!\n\n"
            "Tip: Click 'Restore / Undo' anytime to put them back."
        )

    def restore(self):
        """Undo: put organized files back to their original location."""
        folder = self.get_folder()
        if folder is None:
            return

        history = load_history(folder)
        restored = 0

        # ---- Case 1: history log exists -> precise restore ----
        if history:
            if not messagebox.askyesno(
                "Restore", f"Restore {len(history)} file(s) to their original location?"
            ):
                return

            self.clear_log()
            for entry in reversed(history):
                src = Path(entry["moved_to"])
                dst = Path(entry["original"])
                if not src.is_file():
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                target = unique_path(dst)
                shutil.move(str(src), str(target))
                self.add_row(target.name, src.parent.name + "/", "original location")
                restored += 1
                self.set_status(f"Restoring... {restored}/{len(history)}", C_PURPLE)
                self.root.update_idletasks()

            clear_history(folder)

        # ---- Case 2: no history (older version) -> move everything back ----
        else:
            found = []
            for cat in CATEGORIES:
                d = folder / cat
                if d.is_dir():
                    found += [(cat, f) for f in sorted(d.iterdir()) if f.is_file()]

            if not found:
                messagebox.showinfo("Info", "Nothing to restore in this folder.")
                return
            if not messagebox.askyesno(
                "Restore",
                f"No history file found.\n\nMove ALL {len(found)} file(s) from the "
                "category folders back to:\n" + str(folder)
            ):
                return

            self.clear_log()
            for cat, f in found:
                target = unique_path(folder / f.name)
                shutil.move(str(f), str(target))
                self.add_row(target.name, cat + "/", "this folder")
                restored += 1
                self.set_status(f"Restoring... {restored}/{len(found)}", C_PURPLE)
                self.root.update_idletasks()

        # ---- Remove now-empty category folders ----
        removed_dirs = 0
        for cat in CATEGORIES:
            d = folder / cat
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                removed_dirs += 1

        self.check_history()
        self.set_status(f"Restored! {restored} file(s) back to the original folder.",
                        C_GREEN)
        messagebox.showinfo(
            "Restore Complete",
            f"{restored} file(s) restored.\n{removed_dirs} empty folder(s) cleaned up."
        )


def main():
    root = Tk()
    FileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
