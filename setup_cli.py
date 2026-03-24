"""
DeepRAG setup CLI.

Usage::

    uv run setup_cli.py
"""

import sys
import time

# ─── ANSI codes ───

ESC = "\033"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"
CLEAR_LINE = f"{ESC}[2K\r"

CURSOR_BLOCK = f"{ESC}[2 q"
CURSOR_RESET = f"{ESC}[0 q"
CURSOR_COLOR_SET = f"{ESC}]12;#c8c4c0\007"
CURSOR_COLOR_RESET = f"{ESC}]112\007"

C_WHITE = f"{ESC}[38;2;255;255;255m"
C_STONE_200 = f"{ESC}[38;2;231;229;228m"
C_STONE_400 = f"{ESC}[38;2;168;162;158m"
C_STONE_600 = f"{ESC}[38;2;87;83;78m"
C_AMBER = f"{ESC}[38;2;214;170;94m"
C_RESET = f"{ESC}[0m"

# ─── Terminal setup / teardown ───

def setup_terminal():
    sys.stdout.write(CURSOR_BLOCK)
    sys.stdout.write(CURSOR_COLOR_SET)
    sys.stdout.flush()


def restore_terminal():
    sys.stdout.write(CURSOR_RESET)
    sys.stdout.write(CURSOR_COLOR_RESET)
    sys.stdout.flush()


# ─── Logo ───

LOGO_LINES = [
    "██████   ████████  ████████  ██████   ██████     ████    ██████  ",
    "██   ██  ██        ██        ██   ██  ██   ██   ██  ██  ██      ",
    "██   ██  ██████    ██████    ██████   ██████    ██████  ██  ███  ",
    "██   ██  ██        ██        ██       ██  ██    ██  ██  ██   ██  ",
    "██████   ████████  ████████  ██       ██   ██   ██  ██  ██████   ",
]

LOGO_GRADIENT = [
    C_WHITE,
    C_STONE_200,
    C_AMBER,
    C_STONE_400,
    C_STONE_600,
]


def animate_logo():
    sys.stdout.write(HIDE_CURSOR)
    max_width = max(len(line) for line in LOGO_LINES)
    height = len(LOGO_LINES)

    for _ in range(height):
        print()

    for col in range(max_width + 1):
        sys.stdout.write(f"{ESC}[{height}A")
        for i, line in enumerate(LOGO_LINES):
            partial = line[:col]
            grad = LOGO_GRADIENT[i % len(LOGO_GRADIENT)]
            sys.stdout.write(f"{CLEAR_LINE}    {grad}{partial}{C_RESET}\n")
        sys.stdout.flush()
        time.sleep(0.008)

    sys.stdout.write(SHOW_CURSOR)


# ─── Main ───

def main():
    try:
        setup_terminal()
        print()
        animate_logo()
        print()

    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        restore_terminal()
        print()
        sys.exit(0)
    finally:
        restore_terminal()


if __name__ == "__main__":
    main()
