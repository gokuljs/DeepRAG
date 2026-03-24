"""
Interactive setup wizard for Deep RAG.

Walks you through installation, API key configuration, index building,
and runs a demo search so you can see it all working.

Usage::

    uv run cli/setup_cli.py
"""

import os
import sys
import subprocess
import time

LOGO = r"""
    ____                    ____  ___   ______
   / __ \___  ___  ____   / __ \/   | / ____/
  / / / / _ \/ _ \/ __ \ / /_/ / /| |/ / __
 / /_/ /  __/  __/ /_/ // _, _/ ___ / /_/ /
/_____/\___/\___/ .___//_/ |_/_/  |_\____/
               /_/
"""

BEAR = r"""
        .--.              .--.
       : (\ ". _......_ ." /) :
        '.    `        `    .'
         .'    _    _    '.
        /     (_)  (_)     \
       |       _    _       |
       |      (_)  (_)      |
        \     ._    _.     /
         '.   /  '--'  \  .'
           '-|          |-'
             \   .--.   /
              '._/  \._'
"""

COLORS = {
    "green": "\033[92m",
    "blue": "\033[94m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def color(text, c):
    return f"{COLORS[c]}{text}{COLORS['reset']}"


def print_step(num, total, msg):
    print(f"\n{color(f'[{num}/{total}]', 'cyan')} {color(msg, 'bold')}")


def print_success(msg):
    print(f"  {color('✓', 'green')} {msg}")


def print_info(msg):
    print(f"  {color('→', 'blue')} {msg}")


def print_warn(msg):
    print(f"  {color('!', 'yellow')} {msg}")


def print_error(msg):
    print(f"  {color('✗', 'red')} {msg}")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n  {color('Press Enter to continue...', 'dim')}")


def show_welcome():
    clear_screen()
    print(color(LOGO, "cyan"))
    print(color("  How search actually works, and why it evolved the way it did.", "bold"))
    print(color("  Every retrieval algorithm exists because the previous one had a flaw.", "dim"))
    print()
    print(color(BEAR, "yellow"))
    print(color("  Welcome to the Deep RAG setup wizard.", "green"))
    print(color("  This will get everything configured and running.\n", "dim"))
    pause()


def check_uv():
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"uv is installed ({version})")
            return True
    except FileNotFoundError:
        pass
    print_error("uv is not installed")
    print_info("Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh")
    print_info("Or with Homebrew: brew install uv")
    return False


def install_dependencies():
    print_info("Running uv sync...")
    result = subprocess.run(
        ["uv", "sync"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    if result.returncode == 0:
        print_success("All dependencies installed")
        return True
    else:
        print_error("Failed to install dependencies")
        print(f"    {result.stderr}")
        return False


def setup_api_key():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

    existing_key = None
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    existing_key = line.strip().split("=", 1)[1]

    if existing_key and existing_key != "your_gemini_api_key_here":
        masked = existing_key[:8] + "..." + existing_key[-4:]
        print_success(f"Gemini API key already configured ({masked})")
        change = input(f"  {color('→', 'blue')} Want to change it? [y/N]: ").strip().lower()
        if change != "y":
            return True

    print_info("You need a Gemini API key for query enhancement, reranking, and RAG generation.")
    print_info("Get one at: https://aistudio.google.com/apikey")
    print()
    key = input(f"  {color('→', 'blue')} Paste your Gemini API key (or press Enter to skip): ").strip()

    if not key:
        print_warn("Skipped. You can add it later to .env as GEMINI_API_KEY=your_key")
        return False

    lines = []
    key_written = False
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={key}\n")
                    key_written = True
                else:
                    lines.append(line)

    if not key_written:
        lines.append(f"GEMINI_API_KEY={key}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)

    print_success("API key saved to .env")
    return True


def build_index():
    print_info("Building BM25 inverted index from movie corpus...")
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(cli_dir)
    result = subprocess.run(
        ["uv", "run", "cli/keyword_search_cli.py", "build"],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )
    if result.returncode == 0:
        print_success("BM25 index built and cached")
        return True
    else:
        print_error("Failed to build index")
        if result.stderr:
            print(f"    {result.stderr[:200]}")
        return False


def embed_chunks():
    print_info("Embedding document chunks (this downloads the model on first run)...")
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(cli_dir)
    result = subprocess.run(
        ["uv", "run", "cli/semantic_search-cli.py", "embedchunks"],
        capture_output=True,
        text=True,
        cwd=project_dir,
        timeout=300,
    )
    if result.returncode == 0:
        print_success("Chunks embedded and cached")
        return True
    else:
        print_error("Failed to embed chunks")
        if result.stderr:
            print(f"    {result.stderr[:200]}")
        return False


def run_demo():
    print_info("Running a demo search: \"sci-fi adventure in space\"")
    print()
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(cli_dir)
    result = subprocess.run(
        ["uv", "run", "cli/hybrid_search_cli.py", "rrfsearch", "sci-fi adventure in space", "--limit", "5"],
        capture_output=True,
        text=True,
        cwd=project_dir,
        timeout=120,
    )
    if result.returncode == 0 and result.stdout.strip():
        for line in result.stdout.strip().split("\n"):
            print(f"    {line}")
        print()
        print_success("Search is working")
        return True
    else:
        print_warn("Demo search didn't return results, but setup is complete")
        if result.stderr:
            print(f"    {result.stderr[:200]}")
        return False


def show_next_steps():
    print(f"\n{color('All done! Here are some things to try:', 'bold')}\n")
    commands = [
        ("BM25 search", 'uv run cli/keyword_search_cli.py bm25search "space adventure"'),
        ("Semantic search", 'uv run cli/semantic_search-cli.py search "a movie about loneliness"'),
        ("Hybrid + rerank", 'uv run cli/hybrid_search_cli.py rrfsearch "space western" --rerank-method cross-encoder'),
        ("RAG generation", 'uv run cli/augmented_generation_cli.py rag "what are some good space movies?"'),
        ("Image search", "uv run cli/multimodal_search_cli.py image_search cli/data/bear.jpg"),
        ("Evaluation", "uv run cli/evaluation_cli.py evaluate --limit 3"),
    ]
    for name, cmd in commands:
        print(f"  {color(name, 'cyan')}")
        print(f"  {color(cmd, 'dim')}\n")


def main():
    show_welcome()
    total = 5

    print_step(1, total, "Checking uv installation")
    if not check_uv():
        print_error("Please install uv first and re-run this setup.")
        sys.exit(1)

    print_step(2, total, "Installing dependencies")
    if not install_dependencies():
        print_error("Dependency installation failed. Check the errors above.")
        sys.exit(1)

    print_step(3, total, "Gemini API key")
    has_key = setup_api_key()

    print_step(4, total, "Building search indexes")
    if not build_index():
        print_error("Index build failed. You can retry with: uv run cli/keyword_search_cli.py build")
        sys.exit(1)

    embed = input(f"\n  {color('→', 'blue')} Embed document chunks now? This takes a minute on first run. [Y/n]: ").strip().lower()
    if embed != "n":
        embed_chunks()

    print_step(5, total, "Running demo search")
    run_demo()

    show_next_steps()

    if not has_key:
        print_warn("Remember to add your Gemini API key to .env for LLM features.\n")


if __name__ == "__main__":
    main()
