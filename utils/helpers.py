# utils/helpers.py

from datetime import datetime, timezone


def get_current_utc_datetime():
    """
    Returns the current date and time in UTC format.

    Returns:
    - str: The current UTC date and time as a formatted string.
    """
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime("%Y-%m-%d %H:%M:%S.%f UTC")[:-3]
