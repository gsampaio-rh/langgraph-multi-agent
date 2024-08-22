import curses
import time
from utils.log_utils import log_storage  # Import the actual log storage
import re

# Define the regex pattern for agent log lines
log_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - \[\w+\] \w+: .*")


# The curses UI that runs in the terminal
def curses_ui(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()

    log_lines = []  # Collect all logs in one place

    while True:
        stdscr.clear()  # Clear the screen before every refresh

        height, width = stdscr.getmaxyx()

        # Collect all logs from all agents
        for logs in log_storage.values():
            log_lines.extend(logs)

        # Only keep the number of logs that fit on the screen
        log_lines = log_lines[-height:]

        # Print each log line, making sure it fits within the screen width
        for idx, log in enumerate(log_lines):
            stdscr.addstr(idx, 0, log[:width])

        stdscr.refresh()  # Refresh the screen to display changes
        time.sleep(0.1)
