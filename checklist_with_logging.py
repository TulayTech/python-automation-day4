"""
DAY 4:
Checklist App + Integrated Logger + Export Reports

WHAT THIS SCRIPT DOES (high-level):
- Reuses the Day 3 logger so everything the user does is written to BOTH:
    1) The TERMINAL (real-time feedback)
    2) A LOG FILE (persistent history) that rotates daily, keeping 7 backups

- Runs the Day 2 checklist app (add, show, mark complete, remove) but now:
  *Every action is logged* with timestamps and levels.

- Adds a new option: "Export Logs" to generate a human-friendly report
    from the log file in one of three formats: Markdown (.md), CSV (.csv), or plain text (.txt).

WHY THIS MATTERS:
- In professional QA, logs are an audit trail: who did what, when, and what happened.
- Exporting logs lets you share results with managers or attach to tickets.

FILES/FOLDERS IT USES/CREATES:
- logs/test_results.log     (rolling daily log, created automatically)
- day4_checklist.json       (checklist persistence)
- reports/                  (where exported reports are written)
"""

# ----------------------------
# IMPORTS
# ----------------------------
from pathlib import Path                            # Safer, cross-platform file paths
import json                                         # Save/load checklist as JSON
import logging                                      # Core logging framework
import sys                                          # To explicitly route console logs to stdout (Display)
from logging.handlers import TimedRotatingFileHandler
import argparse                                     # Add --verbose flag for debug-level console logs
import re                                           # Used to parse log lines for export
from datetime import datetime                       # For timestamping export filenames

# ----------------------------
# PATHS
# ----------------------------
PROJECT_DIR   = Path(__file__).resolve().parent       # File path to where this script lives
DATA_FILE     = PROJECT_DIR / "day4_checklist.json"   # Checklist storage
LOG_DIR       = PROJECT_DIR / "logs"                  # Folder for all log files
LOG_FILE      = LOG_DIR / "test_results.log"          # Main rotating log file
REPORTS_DIR   = PROJECT_DIR / "reports"               # Where we save exported reports


# ----------------------------
# LOGGER CONFIG
# ----------------------------
"""
    Build and return a logger that emits to BOTH the console (live) and a daily-rotating file (history).

    NOTE:
    - Think of the logger as a "hub".
    - You send messages to the hub (logger.info(...)/log files).
    - The hub forwards the message to one or more "handlers" (the console, or file).
    - Each handler has its own level and its own destination.
    - A formatter keeps lines clean for better UI: timestamp | level | logger | message.
"""

def configure_logger(verbose: bool = False) -> logging.Logger:
    # logger process level: DEBUG when --verbose is used in terminal. - INFO by default
    logLevel = logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Verify log exists (parent = True), creates any missing folder in path
    # exist_ok = True (if already exists, thats ok, avoid crashing)

    LOG_DIR.mkdir(parents = True, exist_ok = True)

    # Name for the logs, helps with filtering and identifying
    logger = logging.getLogger("checklist_day4")

    # Removes old handler to prevent duplicates, if configure_logger is called multiple times
    if logger.handlers:
        for handlers in list(logger.handlers):
            logger.removeHandler(handlers)

    # Set logger process level. DEBUG when --verbose is used in terminal. - INFO by default
    logLevel()

    # Logs format for better UI
    logsFormat = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler in real-time
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logLevel())
    console_handler.setFormatter(logsFormat)

    # File handler: Keeps logs historical record and rotates daily. Keeps the last 7 files
    file_handler = TimedRotatingFileHandler(
        filename = str(LOG_FILE),
        when = "midnight",      # Rotates at midnight
        interval = 1,           # Every day
        backupCount = 7,        # Keeps teh last 7 files
        encoding = "utf-8",     # Helps encoding text using (Unicode Transformation Format)
        utc = False             # Use local time
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_handler)

    # Outputs to console and file/directory
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# ----------------------------
# LOG DATA: load/save checklist
# ----------------------------

"""
Tries to load existing checklist from JSON file.
If missing or invalid, return an empty list to prevent app from crashing.
"""
def load_checklist() -> list[dict]: # Single-purpose function: returns current checklist as a list of dictionaries
    if not DATA_FILE.exists(): # Checks if "day4_checklist.json file exists"
        return [] # If not, start with empty list (do not crash)
    try:
        text = DATA_FILE.read_text(encoding = "utf-8") # reads file as a string using "utf-8"
        data = json.loads(text) # Parse JSON string as readable python data (list/dictionaries)
        if isinstance(data, list) and all(isinstance(i, dict) for i in data):
            return data
        print("⚠️ Checklist file found, but the format looked unexpected. Starting clean...")
        return []
    except Exception as error:
        print(f"⚠️ Could not read checklist file: {error}. Starting clean...")
        return []

"""
Saves the entire checklist to JSON file to keep progress between runs.
"""
def save_checklist(items: list[dict]) -> None:
    try:
        DATA_FILE.write_text(json.dumps(items, indent = 2), encoding = "utf-8")
    except Exception as error:
        print(f"❌ Could not save checklist: {error}")

# ----------------------------
# UI helpers
# ----------------------------

"""
Prints menu option every loop to give the user choices
"""
def show_menu() -> None:
    print("\n==== CHECKLIST + LOGGER ====")
    print("1) Add a new checklist item")
    print("2) Show all items")
    print("3) Mark an item as complete")
    print("4) Remove an item (by number OR name)")
    print("5) Export logs to report (md/csv/txt)")
    print("6) Exit")