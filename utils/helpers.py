# utils/helpers.py
import os
import time
import sys
from datetime import datetime, timezone

def get_current_utc_datetime():
    """
    Returns the current date and time in UTC format.

    Returns:
    - str: The current UTC date and time as a formatted string.
    """
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime("%Y-%m-%d %H:%M:%S.%f UTC")[:-3]

def get_file_content(file_path):
    """
    Opens a file from the specified path and retrieves its content.

    Args:
    - file_path (str): The path to the file.

    Returns:
    - str: The content of the file as a string.

    Raises:
    - FileNotFoundError: If the file does not exist at the specified path.
    - IOError: If there is an issue reading the file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")

def loading_animation(cycles=3, duration=0.2):
    """A simple loading animation (rotating bar)."""
    for _ in range(cycles):
        for frame in r"-\|/":
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(duration)
