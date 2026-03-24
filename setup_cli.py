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

# ── Cream / Orange palette ────────────────────────────────────────────────────
#
#   bg     #0a0a0a   soft black
#   ── logo gradient (top → bottom) ──
#   row 0  #faf3e1   near-white cream
#   row 1  #f5e7c6   warm linen
#   row 2  #ff6d1f   bright orange
#   row 3  #8b3510   burnt sienna (interpolated)
#   row 4  #222222   near-black dark gray
#   ── text / ui ──
#   body   #faf3e1   warm cream
#   dim    #8b3510   burnt sienna muted
#   accent #ff6d1f   bright orange
#   red    #ff6d1f   same
# ─────────────────────────────────────────────────────────────────────────────

# OSC 10/11
TERM_BG_SET   = f"{ESC}]11;#0a0a0a\007"
TERM_FG_SET   = f"{ESC}]10;#faf3e1\007"
TERM_BG_RESET = f"{ESC}]111\007"
TERM_FG_RESET = f"{ESC}]110\007"

# OSC 12 — cursor: orange
CURSOR_COLOR_SET   = f"{ESC}]12;#ff6d1f\007"
CURSOR_COLOR_RESET = f"{ESC}]112\007"

BG = f"{ESC}[48;2;10;10;10m"          # #0a0a0a

# Logo gradient — white → cream → cream-orange → light orange → dark orange
C_W1 = f"{ESC}[38;2;253;248;238m"    # #fdf8ee  near white
C_W2 = f"{ESC}[38;2;245;231;198m"    # #f5e7c6  warm cream
C_W3 = f"{ESC}[38;2;240;198;130m"    # #f0c682  creamy orange
C_W4 = f"{ESC}[38;2;232;148;64m"     # #e89440  light orange
C_W5 = f"{ESC}[38;2;192;90;24m"      # #c05a18  darker orange

# UI colours
C_GREEN = f"{ESC}[38;2;255;109;31m"   # #ff6d1f  orange accent
C_DIM   = f"{ESC}[38;2;139;53;16m"    # #8b3510  burnt sienna muted
C_BODY  = f"{ESC}[38;2;250;243;225m"  # #faf3e1  warm cream body
C_RED   = f"{ESC}[38;2;255;109;31m"   # #ff6d1f  orange for errors

# Aliases
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

LOGO_GRADIENT = [C_W1, C_W2, C_W3, C_W4, C_W5]   # gold → fire → ember


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

# Creamy orange — sits between warm cream and light orange, soft and warm
C_SUBTITLE = f"{ESC}[38;2;238;185;110m"   # #eeb96e  creamy orange

SUBTITLE = [
    ("Every retrieval algorithm exists because the previous one had a flaw.",  C_SUBTITLE, 0.020),
    ("I traced all of them. Built each one from scratch to understand why.",   C_SUBTITLE, 0.018),
    ("No frameworks. No wrappers. This CLI is how you play with the result.",  C_SUBTITLE, 0.018),
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
