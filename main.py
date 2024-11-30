# main.py

import curses
import time
from layout import render_header, render_table, render_footer
from process_info import get_system_info, get_process_info
import psutil
import json
import datetime
import os
import sys

def load_ascii_art(filename):
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(application_path, filename)
    try:
        with open(file_path, 'r') as f:
            ascii_art = f.read().splitlines()
    except FileNotFoundError:
        ascii_art = []
    return ascii_art


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True)        # Don't block on getch()
    stdscr.timeout(50)          # Refresh every 50ms
    stdscr.keypad(True)         # Enable keypad mode to capture special keys

    # Enable mouse events
    curses.mousemask(curses.BUTTON1_CLICKED)

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)     # Header and footer
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Table header
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected row
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Regular rows
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Sorted column header

    scroll_position = 0
    selected_row = 0
    process_list = []
    system_info = {}
    last_refresh_time = 0
    need_refresh = True
    search_term = ''
    sort_column = None
    sort_reverse = False
    footer_message = ''
    footer_message_time = 0

    # Load ASCII art
    ascii_art = load_ascii_art('ascii_art.txt')

    # Column definitions
    columns = ['PID', 'USER', 'CPU%', 'MEM%', 'TIME', 'STATUS', 'THRDS', 'NICE', 'COMMAND']
    col_keys = ['pid', 'username', 'cpu_percent', 'mem_percent', 'time', 'status', 'num_threads', 'nice', 'exe']
    col_widths = [6, 10, 6, 6, 10, 10, 6, 4, None]  # COMMAND column width will be calculated

    while True:
        current_time = time.time()
        # Update data every 1 second or if needed
        if need_refresh or current_time - last_refresh_time > 1:
            system_info = get_system_info()
            process_list = get_process_info()
            # Apply search filter
            if search_term:
                process_list = [proc for proc in process_list if search_term.lower() in proc['name'].lower() or search_term.lower() in proc['exe'].lower()]
            # Apply sorting
            if sort_column:
                process_list.sort(key=lambda x: x.get(sort_column) if x.get(sort_column) is not None else 0, reverse=sort_reverse)
            last_refresh_time = current_time
            need_refresh = False

        # Check if footer_message needs to be cleared
        if footer_message and current_time - footer_message_time > 5:
            footer_message = ''
            need_refresh = True

        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxyx()
        # Recalculate header, table, footer sizes
        header_height = 4 + len(ascii_art)  # Fixed header height plus ASCII art
        footer_height = 1
        table_height = max_y - header_height - footer_height - 2  # -2 for table header and padding

        # Calculate column positions
        total_fixed_width = sum(col_widths[:-1]) + len(col_widths) - 1  # sum of widths + spaces between columns
        col_widths[-1] = max_x - total_fixed_width - 1  # Remaining width for COMMAND
        x = 0
        col_positions = []
        for idx, width in enumerate(col_widths):
            col_positions.append((col_keys[idx], x, x + width))
            x += width + 1  # +1 for space

        stdscr.erase()

        render_header(stdscr, system_info, max_x, ascii_art)

        start_row = header_height  # Header is fixed height
        render_table(stdscr, process_list, start_row, table_height, scroll_position, max_x, selected_row, sort_column, sort_reverse, col_positions, columns, col_keys, col_widths)

        render_footer(stdscr, max_y, footer_height, max_x, footer_message)

        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key != -1:
                if key == ord('q'):
                    break  # Exit the loop
                elif key == curses.KEY_DOWN:
                    if selected_row < len(process_list) - 1:
                        selected_row += 1
                        if selected_row >= scroll_position + table_height:
                            scroll_position += 1
                elif key == curses.KEY_UP:
                    if selected_row > 0:
                        selected_row -= 1
                        if selected_row < scroll_position:
                            scroll_position -= 1
                elif key == ord('k'):
                    selected_proc = process_list[selected_row]
                    pid_to_kill = selected_proc['pid']
                    try:
                        p = psutil.Process(pid_to_kill)
                        p.kill()
                        # Force data refresh
                        need_refresh = True  
                    except psutil.AccessDenied:
                        # Can't kill the process
                        pass
                    except psutil.NoSuchProcess:
                        # Process no longer exists
                        need_refresh = True  # Force data refresh
                elif key == ord('/'):
                    # Search 
                    stdscr.nodelay(False)  # wait for user input
                    curses.echo()
                    stdscr.addstr(max_y - 2, 0, "Search: ")
                    stdscr.clrtoeol()
                    search_term_input = stdscr.getstr().decode()
                    curses.noecho()
                    stdscr.nodelay(True)  # Turn nodelay back on
                    search_term = search_term_input.strip()
                    need_refresh = True
                    selected_row = 0
                    scroll_position = 0
                elif key == ord('h'):
                    # Display help screen
                    show_help_screen(stdscr, max_y, max_x)
                    need_refresh = True
                elif key == ord('d'):
                    # Display process details
                    if len(process_list) > 0:
                        selected_proc = process_list[selected_row]
                        show_process_details(stdscr, selected_proc)
                        need_refresh = True
                elif key == ord('e'):
                    # Export process list to a JSON file
                    footer_message = export_process_list(process_list)
                    footer_message_time = time.time()
                    need_refresh = True
                elif key == curses.KEY_MOUSE:
                    # Handle mouse click
                    _, mx, my, _, _ = curses.getmouse()
                    if my == start_row:
                        # Clicked on header row
                        for idx, (col_key, x_start, x_end) in enumerate(col_positions):
                            if x_start <= mx <= x_end:
                                if sort_column == col_key:
                                    sort_reverse = not sort_reverse
                                else:
                                    sort_column = col_key
                                    sort_reverse = False
                                need_refresh = True
                                selected_row = 0
                                scroll_position = 0
                                break
        except curses.error:
            pass

        # Adjust selected_row and scroll_position if necessary
        if selected_row >= len(process_list):
            selected_row = len(process_list) - 1
        if selected_row < 0:
            selected_row = 0
        if scroll_position > selected_row:
            scroll_position = selected_row
        if scroll_position < 0:
            scroll_position = 0
        if scroll_position + table_height > len(process_list):
            scroll_position = max(0, len(process_list) - table_height)

        # Sleep a bit
        time.sleep(0.05)

def load_ascii_art(filename):
    try:
        with open(filename, 'r') as f:
            ascii_art = f.read().splitlines()
    except FileNotFoundError:
        ascii_art = []
    return ascii_art

def show_help_screen(stdscr, max_y, max_x):
    # Clear screen
    stdscr.clear()
    help_text = [
        "Help Screen - Controls and Features",
        "",
        "Up/Down arrows: Navigate through the process list",
        "'k': Kill the selected process",
        "'/': Search processes by name or command",
        "Click column headers to sort by that column",
        "'d': Show details of the selected process",
        "'e': Export process list to JSON file",
        "'h': Show this help screen",
        "'q': Quit the application",
        "",
        "Press any key to return to the main screen..."
    ]
    for idx, line in enumerate(help_text):
        if idx >= max_y - 1:
            break
        stdscr.addstr(idx, 0, line[:max_x])
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)

def show_process_details(stdscr, proc):
    # Clear screen
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    try:
        p = psutil.Process(proc['pid'])
        details = [
            f"Process Details (PID: {p.pid})",
            "",
            f"Name: {p.name()}",
            f"Executable: {p.exe()}",
            f"Status: {p.status()}",
            f"Started: {time.ctime(p.create_time())}",
            f"CPU Usage: {p.cpu_percent(interval=0.1):.1f}%",
            f"Memory Usage: {p.memory_percent():.1f}%",
            f"Threads: {p.num_threads()}",
            f"Parent PID: {p.ppid()}",
            f"Username: {p.username()}",
            "",
            "Press any key to return to the main screen..."
        ]
        for idx, line in enumerate(details):
            if idx >= max_y - 1:
                break
            stdscr.addstr(idx, 0, line[:max_x])
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        stdscr.addstr(0, 0, f"Could not retrieve details for PID {proc['pid']}: {e}")
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)

def export_process_list(process_list):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"process_monit_out_{timestamp}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(process_list, f, default=str, indent=4)
        message = f"Process list exported to {filename}"
    except Exception as e:
        message = f"Failed to export process list: {e}"
    return message

if __name__ == '__main__':
    curses.wrapper(main)
