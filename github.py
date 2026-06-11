"""
github.py — all GitHub CLI interactions
"""

import subprocess, json, re

REPO = "StabilityNexus/MiniChain"

def gh(endpoint):
    result = subprocess.run(
        ["gh", "api", f"https://api.github.com/{endpoint}"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout)
    except Exception:
        return []

def gh_paginate(endpoint):
    result = subprocess.run(
        ["gh", "api", "--paginate", f"https://api.github.com/{endpoint}"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        return []
    text = result.stdout.strip()
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
    # TEST: last 10 closed. For production use gh_paginate below.
    prs = gh(f"repos/{REPO}/pulls?state=closed&per_page=10&sort=updated&direction=desc")
    return prs if isinstance(prs, list) else []
    # PRODUCTION:
    # return gh_paginate(f"repos/{REPO}/pulls?state=open&per_page=100")

def fetch_pr_files(n):
    files = gh(f"repos/{REPO}/pulls/{n}/files?per_page=100")
    return [f["filename"] for f in files] if isinstance(files, list) else []

def fetch_coderabbit_sections(n):
    """
    Fetch ONLY the Walkthrough and Changes sections from CodeRabbit.
    Everything else (sequence diagrams, poems, tips) is ignored.
    """
    raw = None

    # Check issue comments first
    comments = gh(f"repos/{REPO}/issues/{n}/comments?per_page=50")
    if isinstance(comments, list):
        for c in comments:
            if "coderabbit" in c.get("user", {}).get("login", "").lower() and c.get("body"):
                raw = c["body"]
                break

    # Fallback: PR reviews
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
    """
    Pull only the Walkthrough and Changes table from a CodeRabbit comment.
    CodeRabbit structure:
      ## Walkthrough
      <text>
      ## Changes
      | File | Summary |
      ...
      ## Sequence Diagram(s)   ← stop here
    """
    result = {}

    # Extract Walkthrough section
    wt_match = re.search(
        r"##\s*Walkthrough\s*\n(.*?)(?=\n##\s|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if wt_match:
        result["walkthrough"] = wt_match.group(1).strip()

    # Extract Changes section (table)
    ch_match = re.search(
        r"##\s*Changes\s*\n(.*?)(?=\n##\s|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if ch_match:
        result["changes"] = ch_match.group(1).strip()

    if not result:
        # Fallback: return first 800 chars if structure not found
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