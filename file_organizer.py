"""
Mini File Organizer
-------------------
Organizes files in a folder into subfolders based on their extension.

MCA Mini Project
Modules used: os, shutil, pathlib
"""

import os
import shutil
from pathlib import Path

# Folder name -> file extensions that go inside it
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".java", ".c", ".cpp", ".html", ".css", ".js"],
    "Others": [],  # files with unknown extension go here
}


def get_category(suffix: str) -> str:
    """Return the folder name for a given file extension."""
    suffix = suffix.lower()
    for folder, extensions in CATEGORIES.items():
        if suffix in extensions:
            return folder
    return "Others"


def organize(path: str) -> None:
    """Move every file in `path` into its category subfolder."""
    folder = Path(path)

    if not folder.is_dir():
        print("❌ Folder not found:", path)
        return

    moved = 0
    for item in folder.iterdir():
        # Skip folders and this script itself
        if item.is_dir() or item.name == "file_organizer.py":
            continue

        category = get_category(item.suffix)
        dest_dir = folder / category
        dest_dir.mkdir(exist_ok=True)

        # Avoid overwriting if a file with the same name already exists
        dest = dest_dir / item.name
        if dest.exists():
            stem, suffix = item.stem, item.suffix
            n = 1
            while dest.exists():
                dest = dest_dir / f"{stem}_{n}{suffix}"
                n += 1

        shutil.move(str(item), str(dest))
        moved += 1
        print(f"  {item.name}  →  {category}/")

    print(f"\n✅ Done! {moved} file(s) organized.")


def preview(path: str) -> None:
    """Show what would move where, without actually moving anything."""
    folder = Path(path)
    if not folder.is_dir():
        print("❌ Folder not found:", path)
        return

    print("\n--- Preview (nothing moved yet) ---")
    for item in sorted(folder.iterdir()):
        if item.is_dir() or item.name == "file_organizer.py":
            continue
        print(f"  {item.name}  →  {get_category(item.suffix)}/")
    print()


def main() -> None:
    print("=" * 45)
    print("       MINI FILE ORGANIZER")
    print("=" * 45)

    while True:
        print("\n1. Preview (dry run)")
        print("2. Organize files")
        print("3. Exit")
        choice = input("Choose option (1/2/3): ").strip()

        if choice == "3":
            print("Bye!")
            break
        elif choice in ("1", "2"):
            path = input("Enter folder path: ").strip().strip('"')
            if choice == "1":
                preview(path)
            else:
                organize(path)
        else:
            print("❌ Invalid choice, try again.")


if __name__ == "__main__":
    main()
