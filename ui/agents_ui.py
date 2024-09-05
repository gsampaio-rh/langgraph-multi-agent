import curses

# Agent ASCII Art
AGENT_ART = """
  _________________
 |                 |
 |  o o o o o o o  |
 |  o o o o o o o  |
 |  o o o o o o o  |
 |  o o o o o o o  |
 |  o o o o o o o  |
 |  o o o o o o o  |
 |                 |
 |      _____      |
 |                 |
 |                 |
 |                 |
 |                 |
 |_________________|
"""


def display_agents(stdscr):
    # Clear the screen
    stdscr.clear()

    # Get the dimensions of the terminal
    height, width = stdscr.getmaxyx()

    # Calculate y-position to center vertically
    center_y = height // 2 - 8  # The agent height is around 16 rows, so adjust by half

    # Calculate x-positions to space the agents evenly across the width
    agent_width = 18  # Estimate the width of the agent ASCII art
    spacing = (width - 5 * agent_width) // 6  # Even spacing between 5 agents

    # Define positions for the 5 agents in a horizontal row
    agent_positions = [
        (center_y, spacing),
        (center_y, spacing * 2 + agent_width),
        (center_y, spacing * 3 + agent_width * 2),
        (center_y, spacing * 4 + agent_width * 3),
        (center_y, spacing * 5 + agent_width * 4),
    ]

    # Draw all 5 agents in a horizontal line
    for pos in agent_positions:
        agent_y, agent_x = pos
        for i, line in enumerate(AGENT_ART.splitlines()):
            stdscr.addstr(agent_y + i, agent_x, line)

    # Refresh the screen to show the changes
    stdscr.refresh()

    # Wait for user input to exit
    stdscr.getch()
