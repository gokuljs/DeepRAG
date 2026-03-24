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
#   bg     #050e07   near-black with a green undertone
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
TERM_BG_SET   = f"{ESC}]11;#050e07\007"
TERM_FG_SET   = f"{ESC}]10;#dcfce7\007"
TERM_BG_RESET = f"{ESC}]111\007"
TERM_FG_RESET = f"{ESC}]110\007"

# OSC 12 — cursor colour
CURSOR_COLOR_SET   = f"{ESC}]12;#4ade80\007"
CURSOR_COLOR_RESET = f"{ESC}]112\007"

# Cell background — every printed line carries its own dark canvas so the
# theme is consistent across every terminal regardless of user's bg colour.
BG = f"{ESC}[48;2;5;14;7m"        # #050e07

# Foreground colours
C_MINT   = f"{ESC}[38;2;240;253;244m"   # #f0fdf4  pale mint
C_LIGHT  = f"{ESC}[38;2;134;239;172m"   # #86efac  light green
C_GREEN  = f"{ESC}[38;2;74;222;128m"    # #4ade80  bright green
C_DEEP   = f"{ESC}[38;2;22;163;74m"     # #16a34a  deep green
C_DARK   = f"{ESC}[38;2;5;46;22m"       # #052e16  dark green

C_BODY  = f"{ESC}[38;2;220;252;231m"    # #dcfce7  body text
C_DIM   = f"{ESC}[38;2;22;101;52m"      # #166534  muted
C_RED   = f"{ESC}[38;2;220;38;38m"      # #dc2626  error

C_BOLD  = f"{ESC}[1m"
C_RESET = f"{ESC}[0m"

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

LOGO_GRADIENT = [C_MINT, C_LIGHT, C_GREEN, C_DEEP, C_DARK]

INDENT = "    "


def animate_logo():
    sys.stdout.write(HIDE_CURSOR)
    max_width = max(len(line) for line in LOGO_LINES)
    height    = len(LOGO_LINES)

    # Reserve rows with the dark bg so there's no flicker on first frame
    for _ in range(height):
        sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")

    for col in range(max_width + 1):
        sys.stdout.write(f"{ESC}[{height}A")   # move cursor back up
        for i, line in enumerate(LOGO_LINES):
            partial = line[:col]
            fg      = LOGO_GRADIENT[i]
            # \r   — go to column 0
            # BG   — set cell background for this row
            # text — coloured logo slice
            # ERASE_EOL — fill the rest of the row with BG colour (no fixed width needed)
            sys.stdout.write(f"\r{BG}{INDENT}{fg}{C_BOLD}{partial}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.flush()
        time.sleep(0.008)

    sys.stdout.write(SHOW_CURSOR)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    try:
        setup_terminal()
        os.system("cls" if os.name == "nt" else "clear")
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
