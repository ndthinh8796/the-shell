#!/usr/bin/env python3
import curses


def store_command(cmds):
    with open('.shlog', 'a+') as f:
        for cmd in cmds:
            if cmd:
                if cmd[0] != ' ' and 'exit' not in cmd:
                        f.write(cmd + '\n')


def return_command_line(commands, cmd_line, cursor=''):
    command = [chr(x) for x in commands]
    commands = []
    line = ''.join(command)
    if line:
        if cursor and cursor != len(cmd_line):
            cmd_line[cursor] = line
        elif cmd_line[-1] != line:
            cmd_line.append(line)
    return commands


def take_history():
    try:
        with open('.shlog', 'r') as lines:
            content = lines.read()[:-1]
        cmd_lines = content.split('\n')
    except IOError:
        cmd_lines = ['']
    return cmd_lines


def get_pos(max_list):
    coordinate = curses.getsyx()
    if coordinate not in max_list:
        max_list.append(coordinate)
    return coordinate


def run_reset(line_y, string):
    x = 10
    max = []
    for _ in string:
        max.append((line_y, x))
        x += 1
    return max


def main():
    stdscr = curses.initscr()

    curses.raw()
    stdscr.keypad(True)
    curses.echo()
    curses.noecho()

    y = 0
    x = 10

    lines = take_history()
    list_command = []

    max_range = []

    coordinate = tuple()
    finish_input = True
    line_cursor = len(lines)

    while 'exit' not in lines[-1]:

        stdscr.addstr(y, 0, 'intek-sh$ ')
        y += 1
        finish_input = True

        while finish_input:

            ch = stdscr.getch()
            coordinate = get_pos(max_range)

            # Backspace key
            if ch == 263:
                if coordinate >  (y - 1, 10):
                    # Delete char
                    stdscr.delch(coordinate[0], coordinate[1] - 1)
                    # Print-coordinate - 1
                    x -= 1
                    # Remove char from list command
                    list_command.pop(coordinate[1] - 11)
                    # Reduce max range by 1
                    max_range = max_range[:-1]

            # Enter key
            elif ch == 10:
                # Join list command to make string
                list_command = return_command_line(list_command, lines)
                # Reset line cursor
                line_cursor = len(lines)
                # Row + 1
                y += 1
                # Input start at 10 col
                x = 10
                # Break input
                finish_input = False

            # Left arrow
            elif ch == curses.KEY_LEFT:
                # If cursor is at somewhere > collumn 10
                if coordinate >  (y - 1, 10):
                    # Move cursor to the left
                    stdscr.move(coordinate[0], coordinate[1] - 1)

            # Right arrow
            elif ch == curses.KEY_RIGHT:
                # If cursor is at somewhere < max range
                if coordinate < (y - 1, max_range[-1][1]):
                    # Move cursor to the right
                    stdscr.move(coordinate[0], coordinate[1] + 1)

            # Up arrow
            elif ch == curses.KEY_UP:
                # If cursor > col 11
                if line_cursor > 1:
                    # Save current input
                    return_command_line(list_command, lines, cursor=line_cursor)
                    # Go back line history by 1
                    line_cursor -= 1
                    # Print the line
                    stdscr.addstr(y - 1, 10, lines[line_cursor])
                    # Change list command according to current line
                    list_command = [ord(x) for x in lines[line_cursor]]
                    # Print-coordinate changed according to current line
                    x = 10 + len(lines[line_cursor])
                    # Reset max range of current line
                    max_range =  run_reset(y - 1, lines[line_cursor])
                    # Clear to end of line
                    stdscr.clrtoeol()
                    stdscr.refresh()

            # Down arrow
            elif ch == curses.KEY_DOWN:
                # If cursor is at the end of line history
                if line_cursor < len(lines) - 1:
                    # Save current input
                    return_command_line(list_command, lines, cursor=line_cursor)
                    # Go foward line history by 1
                    line_cursor += 1
                    # Print the line
                    stdscr.addstr(y - 1, 10, lines[line_cursor])
                    # Change list command according to current line
                    list_command = [ord(x) for x in lines[line_cursor]]
                    # Print-coordinate changed according to current line
                    x = 10 + len(lines[line_cursor])
                    # Reset max range of current line
                    max_range =  run_reset(y - 1, lines[line_cursor])
                    # Clear to end of line
                    stdscr.clrtoeol()
                    stdscr.refresh()
                else:
                    # Save current input
                    return_command_line(list_command, lines, cursor=line_cursor)
                    # Input = ''
                    stdscr.addstr(y - 1, 10, '')
                    # Reset list command
                    list_command = []
                    # Reset print-coordinate
                    x = 10
                    # Reset max range
                    max_range = run_reset(y - 1, '')
                    # Clear to end of line
                    stdscr.clrtoeol()
                    stdscr.refresh()

            # Get input as ascii order
            else:
                # If cursor is in the middle of line
                if coordinate < max_range[-1]:
                    max_y = max_range[-1][0]
                    max_x = max_range[-1][1]
                    # Insert character in the cursor position
                    stdscr.insstr(coordinate[0], coordinate[1], chr(ch))
                    # Increase max range x by 1
                    max_range.append((max_y, max_x + 1))
                    # Move cursor to the right
                    stdscr.move(coordinate[0], coordinate[1] + 1)
                    # Append char to list command
                    list_command.insert(coordinate[1] - 11, ch)
                # If cursor is at the end of line
                else:
                    stdscr.addstr(y - 1, x, chr(ch))
                    list_command.append(ch)
                x += 1

    curses.endwin()
    store_command(lines)
    print(lines)
    exit()


if __name__ == "__main__":
    main()
