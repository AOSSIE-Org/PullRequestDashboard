"""
github.py — all GitHub CLI interactions with retry hardening
"""

import subprocess, json, re, time

REPO = "StabilityNexus/MiniChain"
GH_RETRIES     = 3
GH_RETRY_SLEEP = 2  # seconds


def _gh_run(cmd):
    """Run a gh command with retry logic. Returns (returncode, stdout, stderr)."""
    last_err = None
    for attempt in range(1, GH_RETRIES + 1):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result.returncode == 0:
                return result.returncode, result.stdout, result.stderr
            last_err = result.stderr.strip()
        except subprocess.TimeoutExpired:
            last_err = "gh command timed out (60s)"
        except Exception as e:
            last_err = str(e)
        if attempt < GH_RETRIES:
            print(f"    gh retry {attempt}/{GH_RETRIES} — {last_err[:80]}")
            time.sleep(GH_RETRY_SLEEP)
    print(f"    gh failed after {GH_RETRIES} retries: {last_err[:120] if last_err else 'unknown'}")
    return result.returncode, result.stdout, result.stderr


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
    prs = gh(f"repos/{REPO}/pulls?state=closed&per_page=10&sort=updated&direction=desc")
    return prs if isinstance(prs, list) else []


def fetch_pr_files(n):
    files = gh(f"repos/{REPO}/pulls/{n}/files?per_page=100")
    return [f["filename"] for f in files] if isinstance(files, list) else []


def fetch_coderabbit_sections(n):
    """Fetch ONLY the Walkthrough and Changes sections from CodeRabbit comment."""
    raw = None

    comments = gh(f"repos/{REPO}/issues/{n}/comments?per_page=50")
    if isinstance(comments, list):
        for c in comments:
            if "coderabbit" in c.get("user", {}).get("login", "").lower() and c.get("body"):
                raw = c["body"]
                break

    if not raw:
        reviews = gh(f"repos/{REPO}/pulls/{n}/reviews?per_page=50")
        if isinstance(reviews, list):
            for r in reviews:
                if "coderabbit" in r.get("user", {}).get("login", "").lower() and r.get("body"):
                    raw = r["body"]
                    break

    if not raw:
        return None

    return extract_walkthrough_and_changes(raw)


def extract_walkthrough_and_changes(text):
    """Pull only the Walkthrough and Changes table from a CodeRabbit comment."""
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
        result["walkthrough"] = text[:800]
        result["changes"] = ""

    return result


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
