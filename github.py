"""
github.py — all GitHub CLI interactions with retry hardening
"""

import os, subprocess, json, re, time

from config import REPO, PR_STATE, PR_LIMIT, CONTEXT_FILE

GH_RETRIES     = 3
GH_RETRY_SLEEP = 2  # seconds


def _gh_run(cmd, retries=GH_RETRIES, quiet=False):
    """Run a gh command with retry logic. Returns (returncode, stdout, stderr)."""
    code = -1
    stdout = ""
    stderr = ""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result.returncode == 0:
                return result.returncode, result.stdout, result.stderr
            code = result.returncode
            stdout = result.stdout
            stderr = result.stderr
            last_err = result.stderr.strip()
        except subprocess.TimeoutExpired:
            code = -1
            stdout = ""
            stderr = "gh command timed out (60s)"
            last_err = stderr
        except Exception as e:
            code = -1
            stdout = ""
            stderr = str(e)
            last_err = stderr
        if attempt < retries:
            print(f"    gh retry {attempt}/{retries} — {last_err[:80]}")
            time.sleep(GH_RETRY_SLEEP)
    if not quiet:
        print(f"    gh failed after {retries} retries: {last_err[:120] if last_err else 'unknown'}")
    return code, stdout, stderr


def gh(endpoint):
    code, stdout, _ = _gh_run(["gh", "api", f"https://api.github.com/{endpoint}"])
    if code != 0:
        return []
    try:
        return json.loads(stdout)
    except Exception:
        return []


def gh_paginate(endpoint):
    code, stdout, _ = _gh_run(
        ["gh", "api", "--paginate", f"https://api.github.com/{endpoint}"]
    )
    if code != 0:
        return []
    text = stdout.strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            text = "[" + text.replace("][", ",") + "]"
            flat = json.loads(text)
            return [i for sub in flat for i in sub] if flat and isinstance(flat[0], list) else flat
        except Exception:
            return []


def fetch_prs():
    limit = max(1, min(PR_LIMIT, 100))
    prs = gh(f"repos/{REPO}/pulls?state={PR_STATE}&per_page={limit}&sort=updated&direction=desc")
    return prs if isinstance(prs, list) else []


def fetch_pr_files(n):
    files = gh(f"repos/{REPO}/pulls/{n}/files?per_page=100")
    return [f["filename"] for f in files] if isinstance(files, list) else []


_SKIP_PHRASES = (
    "review skipped|skip review|auto reviews are disabled|reviews are disabled|"
    "reviews are blocked|rate limited by coderabbit|rate limit exceeded"
).split("|")


def _is_coderabbit_skip_notice(text: str) -> bool:
    """Return True when the comment preamble is a CodeRabbit status notice."""
    head = text[:250].lower()
    return any(phrase in head for phrase in _SKIP_PHRASES)


def fetch_coderabbit_sections(n):
    """Fetch sections from the first usable CodeRabbit comment or review, skipping
    status notices and falling back to raw text when no sections exist."""
    fallback = None
    for endpoint in (
        f"repos/{REPO}/issues/{n}/comments?per_page=50",
        f"repos/{REPO}/pulls/{n}/reviews?per_page=50",
    ):
        items = gh(endpoint)
        if not isinstance(items, list):
            continue
        for item in items:
            login = item.get("user", {}).get("login", "").lower()
            body = item.get("body")
            if "coderabbit" not in login or not body:
                continue
            if _is_coderabbit_skip_notice(body):
                continue
            sections = extract_walkthrough_and_changes(body)
            if sections:
                return sections
            if fallback is None:
                fallback = {"walkthrough": body[:800], "changes": ""}
    return fallback


def extract_walkthrough_and_changes(text):
    """Extract the Walkthrough and Changes sections, or None if neither exists."""
    result = {}

    wt_match = re.search(
        r"##\s*Walkthrough\s*\n(.*?)(?=\n##\s|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if wt_match:
        result["walkthrough"] = wt_match.group(1).strip()

    ch_match = re.search(
        r"##\s*Changes\s*\n(.*?)(?=\n##\s|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if ch_match:
        result["changes"] = ch_match.group(1).strip()

    if not result:
        return None

    return result


def fetch_repo_context():
    """Project background for the prompts: a local context.md if present, else the target
    repository's AGENTS.md, else its README.md. Returns (text, source)."""
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip(), "context.md"
    for path in ("AGENTS.md", "README.md"):
        cmd = ["gh", "api", "-H", "Accept: application/vnd.github.raw", f"repos/{REPO}/contents/{path}"]
        code, stdout, stderr = _gh_run(cmd, retries=1, quiet=True)
        if code != 0 and "HTTP 404" not in stderr:
            code, stdout, stderr = _gh_run(cmd)  # not a missing file: retry like other gh calls
            if code != 0 and "HTTP 404" not in stderr:
                print(f"  WARNING: could not read {path} from {REPO}; continuing without it")
        if code == 0 and stdout.strip():
            return stdout.strip(), f"{REPO}/{path}"
    return "", None


def extract_linked_issue(body):
    if not body:
        return None
    m = re.search(r"(?:fixes|closes|resolves)\s+#(\d+)", body, re.IGNORECASE)
    return int(m.group(1)) if m else None


def check_gh_auth():
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    return result.returncode == 0
