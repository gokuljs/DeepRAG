"""
DeepRAG setup CLI.

Usage::

    uv run setup_cli.py
"""

import os
import sys
import time

# ─── ANSI primitives ──────────────────────────────────────────────────────────

ESC         = "\033"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"
ERASE_EOL   = f"{ESC}[K"          # erase to end of line using current bg colour
CURSOR_BLOCK = f"{ESC}[2 q"
CURSOR_RESET = f"{ESC}[0 q"

# ── Color palette ─────────────────────────────────────────────────────────────
#
#   bg     #0a0a0a   soft black
#   ── logo gradient (top → bottom) ──
#   row 0  #f0fdf4   pale mint
#   row 1  #86efac   light green
#   row 2  #4ade80   bright green
#   row 3  #16a34a   deep green
#   row 4  #052e16   dark green
#   ── text / ui ──
#   body   #dcfce7   light green-white
#   dim    #166534   muted green
#   accent #4ade80   bright green
#   red    #dc2626   error
# ─────────────────────────────────────────────────────────────────────────────

# OSC 10/11 — terminal fg/bg (iTerm2, kitty, WezTerm; silent no-op elsewhere)
TERM_BG_SET   = f"{ESC}]11;#0a0a0a\007"
TERM_FG_SET   = f"{ESC}]10;#dcfce7\007"
TERM_BG_RESET = f"{ESC}]111\007"
TERM_FG_RESET = f"{ESC}]110\007"

# OSC 12 — cursor colour
CURSOR_COLOR_SET   = f"{ESC}]12;#4ade80\007"
CURSOR_COLOR_RESET = f"{ESC}]112\007"

# Cell background — every printed line carries its own dark canvas so the
# theme is consistent across every terminal regardless of user's bg colour.
BG = f"{ESC}[48;2;10;10;10m"        # #0a0a0a

# Logo gradient — white to dark (top → bottom)
C_W1 = f"{ESC}[38;2;255;255;255m"   # #ffffff  pure white
C_W2 = f"{ESC}[38;2;192;192;192m"   # #c0c0c0  light gray
C_W3 = f"{ESC}[38;2;128;128;128m"   # #808080  mid gray
C_W4 = f"{ESC}[38;2;64;64;64m"      # #404040  dark gray
C_W5 = f"{ESC}[38;2;26;26;26m"      # #1a1a1a  near black

# UI colours — green accents stay
C_GREEN = f"{ESC}[38;2;74;222;128m"    # #4ade80  bright green (spinners, ✓, prompts)
C_DIM   = f"{ESC}[38;2;100;100;100m"   # #646464  muted gray
C_BODY  = f"{ESC}[38;2;220;220;220m"   # #dcdcdc  body text — light gray
C_RED   = f"{ESC}[38;2;220;38;38m"     # #dc2626  error

# Keep aliases so nothing else breaks
C_MINT  = C_W1
C_LIGHT = C_W2
C_DEEP  = C_W4
C_DARK  = C_W5

C_BOLD   = f"{ESC}[1m"
C_ITALIC = f"{ESC}[3m"
C_RESET  = f"{ESC}[0m"

# ─── Terminal setup / teardown ────────────────────────────────────────────────

def setup_terminal():
    sys.stdout.write(TERM_BG_SET)
    sys.stdout.write(TERM_FG_SET)
    sys.stdout.write(CURSOR_BLOCK)
    sys.stdout.write(CURSOR_COLOR_SET)
    sys.stdout.flush()


def restore_terminal():
    sys.stdout.write(C_RESET)
    sys.stdout.write(TERM_BG_RESET)
    sys.stdout.write(TERM_FG_RESET)
    sys.stdout.write(CURSOR_RESET)
    sys.stdout.write(CURSOR_COLOR_RESET)
    sys.stdout.flush()


# ─── Logo ─────────────────────────────────────────────────────────────────────

LOGO_LINES = [
    "██████   ████████  ████████  ██████   ██████     ████    ██████  ",
    "██   ██  ██        ██        ██   ██  ██   ██   ██  ██  ██      ",
    "██   ██  ██████    ██████    ██████   ██████    ██████  ██  ███  ",
    "██   ██  ██        ██        ██       ██  ██    ██  ██  ██   ██  ",
    "██████   ████████  ████████  ██       ██   ██   ██  ██  ██████   ",
]

LOGO_GRADIENT = [C_W1, C_W2, C_W3, C_W4, C_W5]


def _term_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def animate_logo():
    sys.stdout.write(HIDE_CURSOR)
    max_width = max(len(line) for line in LOGO_LINES)
    height    = len(LOGO_LINES)
    pad       = " " * ((_term_width() - max_width) // 2)

    for _ in range(height):
        sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")

    for col in range(max_width + 1):
        sys.stdout.write(f"{ESC}[{height}A")
        for i, line in enumerate(LOGO_LINES):
            partial = line[:col]
            fg      = LOGO_GRADIENT[i]
            sys.stdout.write(f"\r{BG}{pad}{fg}{C_BOLD}{partial}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.flush()
        time.sleep(0.008)

    sys.stdout.write(SHOW_CURSOR)


# ─── Subtitle ─────────────────────────────────────────────────────────────────

SUBTITLE = [
    ("Every retrieval algorithm exists because the previous one had a flaw.",  C_DIM, 0.020),
    ("I traced all of them. Built each one from scratch to understand why.",   C_DIM, 0.018),
    ("No frameworks. No wrappers. This CLI is how you play with the result.",  C_DIM, 0.018),
]


def typewrite(text, fg, delay=0.022):
    tw  = _term_width()
    pad = " " * ((tw - len(text)) // 2)
    for ch in pad + text:
        sys.stdout.write(f"{BG}{C_ITALIC}{fg}{ch}{C_RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()


def animate_subtitle():
    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    for text, fg, delay in SUBTITLE:
        typewrite(text, fg, delay)
    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    try:
        setup_terminal()
        os.system("cls" if os.name == "nt" else "clear")
        for _ in range(3):
            sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.flush()
        animate_logo()
        animate_subtitle()

        # Stay alive in themed mode until Ctrl+C.
        # Steps will go here as they are built out.
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        restore_terminal()
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
