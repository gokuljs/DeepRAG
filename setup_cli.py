"""
DeepRAG setup CLI.

Usage::

    uv run setup_cli.py
"""

import os
import subprocess
import sys
import threading
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


def _term_size():
    try:
        return os.get_terminal_size()
    except OSError:
        return os.terminal_size((80, 24))


def _blank():
    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()


# Global hint bar — paused around every input() so it doesn't interfere
_hint = None


def _input(prompt_str):
    """Write prompt then read input, pausing hint bar so it doesn't clobber."""
    if _hint:
        _hint.pause()
    sys.stdout.write(prompt_str)
    sys.stdout.flush()
    val = input()
    if _hint:
        _hint.resume()
    return val.strip()


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


_skip_anim = threading.Event()


def _watch_for_enter(stop: threading.Event):
    """Poll stdin every 50 ms; set _skip_anim when any key is pressed."""
    try:
        import select as _sel
        while not stop.is_set():
            r, _, _ = _sel.select([sys.stdin], [], [], 0.05)
            if r:
                os.read(sys.stdin.fileno(), 16)   # drain the buffer
                _skip_anim.set()
                return
    except Exception:
        pass


def typewrite(text, fg, delay=0.022):
    tw   = _term_width()
    pad  = " " * ((tw - len(text)) // 2)
    full = pad + text

    # Already skipped — print instantly, no animation
    if _skip_anim.is_set():
        sys.stdout.write(f"\r{BG}{C_ITALIC}{fg}{full}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.flush()
        return

    for idx, ch in enumerate(full):
        if _skip_anim.is_set():
            # Print the rest of this line from the start (clean, no leftover cursor drift)
            sys.stdout.write(f"\r{BG}{C_ITALIC}{fg}{full}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
            sys.stdout.flush()
            return
        sys.stdout.write(f"{BG}{C_ITALIC}{fg}{ch}{C_RESET}")
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()


def animate_subtitle():
    _skip_anim.clear()

    # Disable terminal echo so Enter doesn't print a visible newline mid-animation
    _old_tty = None
    try:
        import termios, tty as _tty
        fd = sys.stdin.fileno()
        _old_tty = termios.tcgetattr(fd)
        _tty.setcbreak(fd)          # char-by-char, no echo, signals (Ctrl-C) still work
    except Exception:
        pass

    stop = threading.Event()
    watcher = threading.Thread(target=_watch_for_enter, args=(stop,), daemon=True)
    watcher.start()

    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    for text, fg, delay in SUBTITLE:
        typewrite(text, fg, delay)
    sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()

    stop.set()
    _skip_anim.clear()

    # Restore terminal settings
    if _old_tty is not None:
        try:
            import termios
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _old_tty)
        except Exception:
            pass

# ─── Helpers ──────────────────────────────────────────────────────────────────

IS_WIN = os.name == "nt"

def _project_dir():
    return os.path.dirname(os.path.abspath(__file__))

def _cache(*parts):
    return os.path.join(_project_dir(), "cli", "cache", *parts)

def _run(cmd, **kwargs):
    """Run a command, returns CompletedProcess. cmd is a list."""
    return subprocess.run(cmd, capture_output=True, text=True,
                          cwd=_project_dir(), **kwargs)

def _print_raw(text):
    sys.stdout.write(f"{BG}  {text}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.flush()


# ─── Hint bar ─────────────────────────────────────────────────────────────────

class HintBar:
    def __init__(self):
        self._stop   = threading.Event()
        self._paused = threading.Event()
        self._thread = None

    def _draw(self):
        rows = _term_size().lines
        sys.stdout.write(
            f"\0337\033[{rows};1H"
            f"{BG}{C_DIM}  ctrl+c to exit{C_RESET}{BG}{ERASE_EOL}{C_RESET}"
            f"\0338"
        )
        sys.stdout.flush()

    def _clear(self):
        rows = _term_size().lines
        sys.stdout.write(f"\0337\033[{rows};1H{C_RESET}{ERASE_EOL}\0338")
        sys.stdout.flush()

    def _loop(self):
        while not self._stop.is_set():
            if not self._paused.is_set():
                self._draw()
            time.sleep(1)

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def pause(self):
        self._paused.set()
        self._clear()

    def resume(self):
        self._paused.clear()
        self._draw()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        self._clear()


# ─── Spinner ──────────────────────────────────────────────────────────────────

class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message):
        self.message = message
        self._stop   = threading.Event()
        self._thread = None

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            f = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(
                f"\r{BG}  {C_GREEN}{f}{C_RESET}{BG}  {C_BODY}{self.message}{C_RESET}{BG}{ERASE_EOL}{C_RESET}"
            )
            sys.stdout.flush()
            i += 1
            time.sleep(0.08)

    def start(self):
        sys.stdout.write(HIDE_CURSOR)
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def done(self, msg):
        self._stop.set(); self._thread.join()
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(
            f"\r{BG}  {C_GREEN}✓{C_RESET}{BG}  {C_BODY}{msg}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()

    def fail(self, msg):
        self._stop.set(); self._thread.join()
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(
            f"\r{BG}  {C_RED}✗{C_RESET}{BG}  {C_BODY}{msg}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()

    def skip(self, msg):
        self._stop.set(); self._thread.join()
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}{msg}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()


# ─── UI helpers ───────────────────────────────────────────────────────────────

def _section(title):
    _blank()
    sys.stdout.write(f"{BG}  {C_GREEN}{C_BOLD}{title}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.write(f"{BG}  {C_DIM}{'─' * 44}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
    _blank()

def _prompt(question):
    return _input(
        f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}{question}{C_RESET}{BG}{ERASE_EOL}{C_RESET}"
    ).lower()


# ─── Install steps ────────────────────────────────────────────────────────────

def step_check_uv():
    s = Spinner("looking for uv...").start()
    time.sleep(0.3)
    try:
        r = _run(["uv", "--version"])
        if r.returncode == 0:
            s.done(r.stdout.strip())
            return True
    except FileNotFoundError:
        pass
    s.fail("uv not found")
    _blank()
    if IS_WIN:
        _print_raw(f"{C_DIM}  winget install astral-sh.uv{C_RESET}")
        _print_raw(f"{C_DIM}  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"{C_RESET}")
    else:
        _print_raw(f"{C_DIM}  curl -LsSf https://astral.sh/uv/install.sh | sh{C_RESET}")
        _print_raw(f"{C_DIM}  brew install uv{C_RESET}")
    _blank()
    return False


def step_install_deps():
    s = Spinner("syncing dependencies...").start()
    r = _run(["uv", "sync"])
    if r.returncode == 0:
        s.done("dependencies synced")
        return True
    s.fail("sync failed")
    if r.stderr:
        _print_raw(f"{C_DIM}{r.stderr.strip()[:300]}{C_RESET}")
    return False


def step_api_key():
    env_path = os.path.join(_project_dir(), ".env")
    existing = None
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    val = line.strip().split("=", 1)[1]
                    if val and val != "your_gemini_api_key_here":
                        existing = val

    if existing:
        masked = existing[:8] + "···" + existing[-4:]
        sys.stdout.write(
            f"\r{BG}  {C_GREEN}✓{C_RESET}{BG}  {C_BODY}api key already set  ({masked}){C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return True

    key = _input(
        f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}gemini api key  (enter to skip): {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
    )

    if not key:
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}skipped — add GEMINI_API_KEY to .env later{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return False

    s = Spinner("writing to .env...").start()
    time.sleep(0.3)
    lines, written = [], False
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={key}\n"); written = True
                else:
                    lines.append(line)
    if not written:
        lines.append(f"GEMINI_API_KEY={key}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)
    s.done("saved to .env")
    return True


def step_build_bm25():
    cache = _cache("index.pkl")
    if os.path.exists(cache):
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}BM25 index already exists, skipping{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return True
    s = Spinner("building inverted index for BM25 search...").start()
    r = _run(["uv", "run", "cli/keyword_search_cli.py", "build"])
    if r.returncode == 0:
        s.done("inverted index built")
        return True
    s.fail("BM25 build failed")
    if r.stderr:
        _print_raw(f"{C_DIM}{r.stderr.strip()[:300]}{C_RESET}")
    return False


def step_build_semantic():
    cache = _cache("chunk_embeddings.npy")
    if os.path.exists(cache):
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}semantic index already exists, skipping{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return True
    s = Spinner("embedding chunks — downloads model on first run...").start()
    try:
        r = _run(["uv", "run", "cli/semantic_search-cli.py", "embedchunks"], timeout=300)
        if r.returncode == 0:
            s.done("semantic index built")
            return True
        s.fail("embedding failed")
        if r.stderr:
            _print_raw(f"{C_DIM}{r.stderr.strip()[:300]}{C_RESET}")
    except subprocess.TimeoutExpired:
        s.fail("timed out  —  run manually: uv run cli/semantic_search-cli.py embedchunks")
    return False


# ── Search types — all 11 modes across 4 categories ──────────────────────────

SEARCH_TYPES = [
    # keyword
    ("1",  "bm25              inverted index, BM25 scoring",             ["uv", "run", "cli/keyword_search_cli.py",       "bm25search"]),
    ("2",  "tfidf             classic TF-IDF keyword search",            ["uv", "run", "cli/keyword_search_cli.py",       "tfidf"]),
    # semantic
    ("3",  "semantic          vector similarity search",                 ["uv", "run", "cli/semantic_search-cli.py",      "search"]),
    ("4",  "chunked semantic  search over sentence-level chunks",        ["uv", "run", "cli/semantic_search-cli.py",      "chunkedsemanticsearch"]),
    # hybrid
    ("5",  "hybrid rrf        BM25 + semantic, reciprocal rank fusion",  ["uv", "run", "cli/hybrid_search_cli.py",        "rrfsearch"]),
    ("6",  "hybrid weighted   BM25 + semantic, weighted sum",            ["uv", "run", "cli/hybrid_search_cli.py",        "ws"]),
    ("7",  "hybrid norm       BM25 + semantic, normalised scores",       ["uv", "run", "cli/hybrid_search_cli.py",        "norm_passed"]),
    # rag  (all require GEMINI_API_KEY)
    ("8",  "rag               retrieve + generate a direct answer",      ["uv", "run", "cli/augmented_generation_cli.py", "rag"]),
    ("9",  "summarize         retrieve + summarize results",             ["uv", "run", "cli/augmented_generation_cli.py", "summarize"]),
    ("10", "citations         retrieve + answer with inline citations",  ["uv", "run", "cli/augmented_generation_cli.py", "citations"]),
    ("11", "q&a               retrieve + answer a specific question",    ["uv", "run", "cli/augmented_generation_cli.py", "question"]),
]

SEARCH_GROUPS = [
    ("keyword",  ["1", "2"]),
    ("semantic", ["3", "4"]),
    ("hybrid",   ["5", "6", "7"]),
    ("rag  ✦ requires gemini api key", ["8", "9", "10", "11"]),
]

RAG_CHOICES = {"8", "9", "10", "11"}


def _gemini_key_valid():
    env_path = os.path.join(_project_dir(), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    val = line.strip().split("=", 1)[1]
                    return bool(val and val != "your_gemini_api_key_here")
    return False


def _show_search_menu():
    _blank()
    for group_name, keys in SEARCH_GROUPS:
        sys.stdout.write(f"{BG}  {C_DIM}{group_name}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        for key, label, _ in SEARCH_TYPES:
            if key in keys:
                sys.stdout.write(
                    f"{BG}  {C_GREEN}{key:>2}{C_RESET}{BG}  {C_BODY}{label}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
                )
        _blank()
    sys.stdout.flush()


def _run_search(query, choice):
    cmd = next((c for k, _, c in SEARCH_TYPES if k == choice), None)
    if not cmd:
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}invalid choice — enter a number from the menu{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return

    # Block RAG calls early if no valid API key
    if choice in RAG_CHOICES and not _gemini_key_valid():
        sys.stdout.write(
            f"\r{BG}  {C_RED}✗{C_RESET}{BG}  {C_BODY}Gemini API key not set or invalid{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.write(
            f"{BG}    {C_DIM}add a real key to .env:  GEMINI_API_KEY=your_key{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return

    _blank()
    s = Spinner(f"running {next(l for k,l,_ in SEARCH_TYPES if k==choice).split()[0]}...").start()
    try:
        r = _run(cmd + [query], timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            s.done("done")
            _blank()
            for line in r.stdout.strip().split("\n"):
                sys.stdout.write(f"{BG}    {C_BODY}{line}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
            _blank()
        else:
            stderr = r.stderr.strip() if r.stderr else ""
            if "GEMINI_API_KEY" in stderr or "API_KEY" in stderr:
                s.fail("Gemini API key is set but was rejected by the API")
            elif "ProxyError" in stderr or "403" in stderr:
                s.fail("network error — model needs internet access on first run")
            elif r.returncode != 0:
                last_err = next(
                    (l for l in reversed(stderr.split("\n")) if l.strip()), ""
                )
                s.fail(f"exited with code {r.returncode}")
                if last_err:
                    _print_raw(f"{C_DIM}{last_err[:200]}{C_RESET}")
            else:
                s.fail("no results — try a different query or search type")
    except subprocess.TimeoutExpired:
        s.fail("timed out — try a simpler query")


def step_try_search():
    _blank()
    query = _input(
        f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}your query (enter to skip): {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
    )
    if not query:
        sys.stdout.write(
            f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}skipped{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
        )
        sys.stdout.flush()
        return

    _show_search_menu()
    choice = _input(
        f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}pick [1-11]: {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
    )
    _run_search(query, choice)

    while True:
        _blank()
        sys.stdout.write(f"{BG}  {C_GREEN}n{C_RESET}{BG}  {C_BODY}new query{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.write(f"{BG}  {C_GREEN}r{C_RESET}{BG}  {C_BODY}same query, different search type{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.write(f"{BG}  {C_GREEN}q{C_RESET}{BG}  {C_BODY}done{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
        _blank()

        action = _input(
            f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}what next? [n/r/q]: {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
        )

        if action == "q":
            break

        elif action == "n":
            new_query = _input(
                f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}your query: {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
            )
            if not new_query:
                sys.stdout.write(
                    f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}query can't be empty{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
                )
                sys.stdout.flush()
                continue
            query = new_query
            _show_search_menu()
            choice = _input(
                f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}pick [1-11]: {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
            )
            _run_search(query, choice)

        elif action == "r":
            _show_search_menu()
            choice = _input(
                f"\r{BG}  {C_GREEN}?{C_RESET}{BG}  {C_BODY}pick [1-11]: {C_RESET}{BG}{ERASE_EOL}{C_RESET}"
            )
            _run_search(query, choice)

        else:
            sys.stdout.write(
                f"\r{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}enter n, r, or q{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
            )
            sys.stdout.flush()


def run_install():
    _section("dependencies")
    if not step_check_uv():
        _print_raw(f"{C_RED}install uv and re-run setup{C_RESET}")
        return False
    if not step_install_deps():
        return False

    _section("api key")
    step_api_key()

    _section("indexes")
    if not step_build_bm25():
        _print_raw(f"{C_RED}retry:  uv run cli/keyword_search_cli.py build{C_RESET}")
        return False
    if _prompt("build semantic index now? downloads model on first run, ~1 min  [Y/n]: ") != "n":
        step_build_semantic()

    _show_cache_summary()

    _section("try a search")
    step_try_search()
    return True


def _show_cache_summary():
    cache_dir = _cache()
    _blank()
    sys.stdout.write(f"{BG}  {C_GREEN}{C_BOLD}what got built{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
    sys.stdout.write(f"{BG}  {C_DIM}{'─' * 44}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n")
    _blank()

    files = [
        ("index.pkl",             "inverted index for BM25 search"),
        ("term_frequency.pkl",    "term frequencies across corpus"),
        ("doc_lengths.pkl",       "document length table"),
        ("docmap.pkl",            "doc id → metadata mapping"),
        ("chunk_embeddings.npy",  "semantic embeddings (vectors)"),
        ("chunk_metadata.json",   "chunk text + source metadata"),
    ]

    for fname, desc in files:
        path = _cache(fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            size_str = f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"
            sys.stdout.write(
                f"{BG}  {C_GREEN}✓{C_RESET}{BG}  {C_BODY}{fname:<28}{C_RESET}{BG}{C_DIM}{desc}  ({size_str}){C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
            )
        else:
            sys.stdout.write(
                f"{BG}  {C_DIM}–{C_RESET}{BG}  {C_DIM}{fname:<28}{desc}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
            )

    _blank()
    sys.stdout.write(
        f"{BG}  {C_DIM}cache:  {cache_dir}{C_RESET}{BG}{ERASE_EOL}{C_RESET}\n"
    )
    _blank()
    sys.stdout.flush()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    global _hint
    _hint = HintBar()
    try:
        setup_terminal()
        os.system("cls" if IS_WIN else "clear")
        for _ in range(3):
            sys.stdout.write(f"{BG}{ERASE_EOL}{C_RESET}\n")
        sys.stdout.flush()
        _hint.start()
        animate_logo()
        animate_subtitle()
        run_install()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        _hint.stop()
        sys.stdout.write(SHOW_CURSOR)
        restore_terminal()
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
