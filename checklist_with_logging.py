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