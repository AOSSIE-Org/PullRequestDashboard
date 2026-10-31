"""
config.py — run settings, from the command line or a .env file

  python main.py owner/repo        analyse that repository's pull requests
  TARGET_REPO=owner/repo           same, set once in .env

Optional .env settings (see .env.example): PR_STATE, PR_LIMIT, OLLAMA_MODEL, OLLAMA_URL.
"""

import os, sys

_ROOT = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv(path):
    """Minimal .env reader (KEY=value lines); real environment variables win."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.split(" #", 1)[0].strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)


_load_dotenv(os.path.join(_ROOT, ".env"))

_args = [a for a in sys.argv[1:] if not a.startswith("-")]
REPO = (_args[0] if _args else os.getenv("TARGET_REPO", "")).strip().strip("/")

PR_STATE     = os.getenv("PR_STATE", "open")          # open, closed or all
PR_LIMIT     = int(os.getenv("PR_LIMIT", "20"))        # most recently updated PRs to analyse (max 100)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Optional hand-written project summary; overrides the target repo's AGENTS.md / README.md.
CONTEXT_FILE = os.path.join(_ROOT, "context.md")


def repo_name():
    return REPO.split("/")[-1] if REPO else "this project"
