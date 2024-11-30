# layout.py

import curses

def render_header(stdscr, system_info, max_x, ascii_art):
    # Set header color
    stdscr.attron(curses.color_pair(1))

    # Fill the entire header area with spaces
    header_height = 4 + len(ascii_art)
    for y in range(header_height):
        stdscr.addstr(y, 0, ' ' * (max_x - 1))

    # Display ASCII art
    for idx, line in enumerate(ascii_art):
        if idx >= 5:  # Limit the ASCII art height
            break
        try:
            stdscr.addstr(idx, 0, line[:max_x])
        except curses.error:
            pass

    # Display bars for CPU, RAM, and SWAP usage
    cpu_percent = system_info['cpu_percent']
    ram_percent = system_info['ram_percent']
    swap_percent = system_info['swap_percent']

    # Max width for bars
    bar_width = max_x - 20 if max_x > 60 else 20  # Ensure minimum width

    # Create bars
    cpu_bar = create_bar(cpu_percent, max_width=bar_width)
    ram_bar = create_bar(ram_percent, max_width=bar_width)
    swap_bar = create_bar(swap_percent, max_width=bar_width)

    header_lines = [
        f"CPU Usage: {cpu_percent:5.1f}% [{cpu_bar}]",
        f"RAM Usage: {ram_percent:5.1f}% [{ram_bar}]",
        f"SWAP Usage: {swap_percent:5.1f}% [{swap_bar}]",
        f"Threads: {system_info['threads']}  |  Uptime: {system_info['uptime']}  |  Battery: {system_info['battery']}"
    ]

    # Display the header lines
    for idx, line in enumerate(header_lines):
        try:
            stdscr.addstr(idx + len(ascii_art), 0, line[:max_x])
        except curses.error:
            pass

    stdscr.attroff(curses.color_pair(1))

def create_bar(percentage, max_width):
    # Create a bar using '█' characters
    bar_length = int((percentage / 100) * max_width)
    bar = '█' * bar_length + ' ' * (max_width - bar_length)
    return bar

def render_table(stdscr, process_list, start_row, table_height, scroll_position, max_x, selected_row, sort_column=None, sort_reverse=False, col_positions=None, columns=None, col_keys=None, col_widths=None):
    # Set table header color
    stdscr.attron(curses.color_pair(2))

    # Build header line
    x = 0
    for idx, col in enumerate(columns):
        col_key = col_keys[idx]
        width = col_widths[idx]
        # Determine if this column is the sorted column
        if sort_column == col_key:
            # Highlight the sorted column header
            stdscr.attron(curses.color_pair(5))  # New color pair for sorted column header
            arrow = '▲' if not sort_reverse else '▼'
            col_title = f"{col}{arrow}"
        else:
            col_title = col
        # Adjust column width to accommodate arrow if necessary
        col_title_formatted = f"{col_title:<{width}}"[:width]
        try:
            stdscr.addstr(start_row, x, col_title_formatted)
        except curses.error:
            pass
        x += width + 1  # +1 for space
        # Reset attributes
        stdscr.attroff(curses.color_pair(5))
    stdscr.attroff(curses.color_pair(2))

    # For each row in table_height, display process info
    for i in range(table_height):
        proc_index = scroll_position + i
        if proc_index >= len(process_list):
            break
        proc = process_list[proc_index]
        x = 0
        # Build the line
        for idx, key in enumerate(col_keys):
            width = col_widths[idx]
            value = proc.get(key, '')
            if key in ['cpu_percent', 'mem_percent']:
                value = f"{value:.1f}"
            elif key == 'nice':
                value = str(value)
            elif key == 'num_threads':
                value = str(value)
            elif key == 'pid':
                value = str(value)
            else:
                value = str(value)
            value_formatted = f"{value:<{width}}"[:width]
            # Highlight selected row
            if proc_index == selected_row:
                stdscr.attron(curses.color_pair(3))
                stdscr.attron(curses.A_BOLD)
            else:
                stdscr.attron(curses.color_pair(4))
            try:
                stdscr.addstr(start_row + 1 + i, x, value_formatted)
            except curses.error:
                pass
            x += width + 1  # +1 for space
            # Turn off attributes
            stdscr.attroff(curses.A_BOLD)
            stdscr.attroff(curses.color_pair(3))
            stdscr.attroff(curses.color_pair(4))

def render_footer(stdscr, max_y, footer_height, max_x, footer_message=''):
    # Set footer color
    stdscr.attron(curses.color_pair(1))

    # Fill the entire footer area with spaces
    for y in range(max_y - footer_height, max_y):
        stdscr.addstr(y, 0, ' ' * (max_x - 1))

    if footer_message:
        footer_text = footer_message
    else:
        footer_text = "Press 'q' to quit | Up/Down to navigate | 'k' to kill | '/' to search | 'd' details | 'h' help | 'e' export"

    # Truncate footer_text if necessary
    if len(footer_text) > max_x:
        footer_text = footer_text[:max_x]

    try:
        stdscr.addstr(max_y - footer_height, 0, footer_text)
    except curses.error:
        pass

    stdscr.attroff(curses.color_pair(1))
