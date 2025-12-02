# organizer.py  ←  FULLY COMMENTED & LABELED EDITION
# -------------------------------------------------------------------
# This script organizes files in a selected folder by file type.
# It sorts files into subfolders (Images, Videos, Documents, etc.)
# and allows UNDOING the sort. It also includes a menu system and
# remembers the chosen folder between sessions using a config file.
# -------------------------------------------------------------------

import shutil                 # Used for moving files
from pathlib import Path      # Easier path handling (better than os.path)
import datetime               # Used for timestamping logs
import sys                    # Used to check for command-line arguments
from collections import defaultdict  # Used to count categories easily

# -------------------------------------------------------------------
# CONFIGURATION HANDLING
# This section loads/saves the folder the user wants to organize.
# -------------------------------------------------------------------

CONFIG_FILE = Path("organizer_config.txt")   # Stores the chosen folder path

def load_folder_from_config():
    """
    Loads the saved folder path from organizer_config.txt.
    If the file doesn't exist or the folder is invalid, user must pick a new one.
    """
    if CONFIG_FILE.exists():
        folder = Path(CONFIG_FILE.read_text(encoding="utf-8").strip())

        # Check if the saved folder is valid
        if folder.exists() and folder.is_dir():
            return folder
        else:
            print(f"\nThe saved folder does not exist anymore:\n{folder}")
            print("You must choose a new folder.\n")
            return set_new_directory()
    else:
        # No config file → ask user for folder
        return set_new_directory()

def set_new_directory():
    """
    Asks the user for a folder path, validates it, saves it into organizer_config.txt,
    and returns the valid folder path.
    """
    while True:
        print("\nEnter the FULL path of the folder you want to organize.")
        new_path = input("Folder path: ").strip().strip('"')  # Remove extra quotes

        # Reject empty input
        if not new_path:
            print("Path cannot be empty.\n")
            continue

        p = Path(new_path)

        # Check if the folder exists
        if not p.exists():
            print("❌ That folder does NOT exist. Try again.\n")
            continue

        # Ensure it's a folder (not a file)
        if not p.is_dir():
            print("❌ That path is NOT a folder. Try again.\n")
            continue

        # Save valid folder path to config file
        CONFIG_FILE.write_text(str(p), encoding="utf-8")

        print(f"\n✔ Folder has been set to:\n  {p}\n")
        return p


# -------------------------------------------------------------------
# LOAD THE SAVED FOLDER
# -------------------------------------------------------------------
SOURCE_FOLDER = load_folder_from_config()

# Log + Undo file paths are always inside the selected folder.
LOG_FOLDER = SOURCE_FOLDER / "Sort_Logs"
UNDO_FILE = LOG_FOLDER / "last_undo.log"


# -------------------------------------------------------------------
# LOGGING FUNCTIONS
# These handle logging all moves and creating the Sort_Logs folder.
# -------------------------------------------------------------------

def ensure_log_folder():
    """Creates the log folder if it doesn't already exist."""
    LOG_FOLDER.mkdir(exist_ok=True)

def log(message):
    """
    Prints a message AND writes it into a timestamped log file.
    Every sorting session gets its own log file.
    """
    print(message)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = LOG_FOLDER / f"log_{timestamp}.txt"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%H:%M:%S}] {message}\n")


# -------------------------------------------------------------------
# CATEGORY DETECTION
# Maps file extensions → categories like Images, Music, etc.
# -------------------------------------------------------------------

def get_category(ext):
    """
    Returns the category name for a given file extension.
    If extension is unknown → goes to "Others".
    """
    ext = ext.lower()

    mapping = {
        # Image formats
        ".png": "Images", ".jpg": "Images", ".jpeg": "Images", ".gif": "Images",
        ".bmp": "Images", ".webp": "Images", ".svg": "Images", ".ico": "Images",
        ".tiff": "Images",

        # Video formats
        ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos",
        ".wmv": "Videos", ".flv": "Videos", ".webm": "Videos", ".m4v": "Videos",

        # Audio/Music formats
        ".mp3": "Music", ".wav": "Music", ".flac": "Music", ".aac": "Music",
        ".ogg": "Music", ".m4a": "Music", ".wma": "Music",

        # Document formats
        ".pdf": "Documents", ".txt": "Documents", ".doc": "Documents",
        ".docx": "Documents", ".xls": "Documents", ".xlsx": "Documents",
        ".ppt": "Documents", ".pptx": "Documents",

        # Programs / installers
        ".exe": "Programs", ".msi": "Programs", ".deb": "Programs",
        ".dmg": "Programs",

        # Compressed archives
        ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
        ".tar": "Archives", ".gz": "Archives", ".bz2": "Archives",
    }

    return mapping.get(ext, "Others")


# -------------------------------------------------------------------
# ORGANIZATION FUNCTION
# Moves each file into its correct category folder.
# Also logs everything AND prepares undo instructions.
# -------------------------------------------------------------------

def organize():
    """Sorts files into category folders and saves undo info."""
    ensure_log_folder()
    log(f"Starting organization of: {SOURCE_FOLDER}")

    moves = []                        # List of (new_path, old_path) used for undo
    category_count = defaultdict(int) # How many files go into each category

    for item in SOURCE_FOLDER.iterdir():
        # Ignore folders and ignore the script itself
        if item.is_file() and item.name != "organizer.py":

            # Determine file category
            category = get_category(item.suffix)

            # Create category folder if needed
            dest_folder = SOURCE_FOLDER / category
            dest_folder.mkdir(exist_ok=True)

            # Destination path
            dest_path = dest_folder / item.name

            # Handle duplicate filenames (file_1.png, file_2.png, etc.)
            if dest_path.exists():
                i = 1
                while dest_path.exists():
                    new_name = f"{item.stem}_{i}{item.suffix}"
                    dest_path = dest_folder / new_name
                    i += 1

            # Actually move the file
            shutil.move(str(item), str(dest_path))

            # Save move details for undo
            moves.append((dest_path, item))
            category_count[category] += 1

            log(f"MOVED: {item.name} → {category}/")

    # Report empty categories to log
    all_categories = {"Images","Videos","Music","Documents","Programs","Archives","Others"}
    for cat in all_categories:
        if category_count[cat] == 0:
            log(f"No {cat.lower()} files were found.")

    total = sum(category_count.values())
    log(f"Organization complete! {total} files moved.\n")

    # Save undo actions to a file
    with open(UNDO_FILE, "w", encoding="utf-8") as f:
        for new_path, old_path in moves:
            f.write(f"{new_path}|{old_path}\n")

    log("Undo info saved.")


# -------------------------------------------------------------------
# UNDO FUNCTION
# Moves everything back where it came from.
# -------------------------------------------------------------------

def undo():
    """Restores all moved files back to their original locations."""
    if not UNDO_FILE.exists():
        print("Nothing to undo — no previous sort found.")
        return

    print("Undoing the last sort...")
    count = 0

    with open(UNDO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            new_path_str, old_path_str = line.split("|", 1)

            new_path = Path(new_path_str)
            old_path = Path(old_path_str)

            # Move file back if it still exists
            if new_path.exists():
                old_path.parent.mkdir(exist_ok=True)
                shutil.move(str(new_path), str(old_path))
                print(f"Restored → {old_path.name}")
                count += 1

    # Remove empty category folders
    for folder_name in ["Images","Videos","Music","Documents","Programs","Archives","Others"]:
        folder = SOURCE_FOLDER / folder_name
        if folder.exists() and not any(folder.iterdir()):
            folder.rmdir()

    # Delete undo file once finished
    UNDO_FILE.unlink()

    print(f"\nUndo complete! {count} files restored.")


# -------------------------------------------------------------------
# MENU SECTION
# Lets the user pick actions from a clean, simple text menu.
# -------------------------------------------------------------------

def show_menu():
    """Displays the main menu."""
    print("=" * 50)
    print(f"   ORGANIZER – Current Folder:")
    print(f"   {SOURCE_FOLDER}")
    print("=" * 50)
    print("1 → Sort / Organize this folder")
    print("2 → Undo last sort")
    print("3 → Change folder directory")
    print("4 → Exit")
    print("-" * 50)


# -------------------------------------------------------------------
# MAIN PROGRAM LOGIC
# Runs the menu loop unless user used --undo via command line.
# -------------------------------------------------------------------

if __name__ == "__main__":

    # Allow quick undo from terminal: python organizer.py --undo
    if len(sys.argv) > 1 and sys.argv[1] == "--undo":
        undo()
    else:
        # Menu loop
        while True:
            show_menu()
            choice = input("Choose (1-4): ").strip()

            # ORGANIZE
            if choice == "1":
                print("\nOrganizing…\n")
                organize()
                input("\nPress Enter to continue…")

            # UNDO
            elif choice == "2":
                print()
                undo()
                input("\nPress Enter to continue…")

            # CHANGE DIRECTORY
            elif choice == "3":
                SOURCE_FOLDER = set_new_directory()
                LOG_FOLDER = SOURCE_FOLDER / "Sort_Logs"
                UNDO_FILE = LOG_FOLDER / "last_undo.log"
                input("\nPress Enter to continue…")

            # EXIT
            elif choice in {"4", "q", "exit", "quit"}:
                print("\nBye!\n")
                break

            # INVALID CHOICE
            else:
                print("Invalid choice — type 1, 2, 3, or 4\n")
