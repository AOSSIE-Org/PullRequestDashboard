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


def is_coderabbit_skip_or_blocked(text: str) -> bool:
    """Check if text is a CodeRabbit skip/blocked/rate-limit notice rather than a review."""
    if not text:
        return True

    # A real review can include a status banner above its walkthrough. Only
    # treat the body as a notice when no usable review sections remain.
    if _has_coderabbit_review_content(text):
        return False

    # CodeRabbit wraps status-only comments in explicit HTML comment markers.
    if re.search(
        r"<!--\s*(?:(?:This is|end of) an auto-generated comment:\s*)?"
        r"(?:skip review|rate limited)\s+by coderabbit\.ai\s*-->",
        text,
        re.IGNORECASE,
    ):
        return True
    if re.search(r"<!--\s*review_access_revoked\s*-->", text, re.IGNORECASE):
        return True

    # Status headings and blockquoted status lines, rather than phrases that
    # can legitimately appear inside a normal review.
    return bool(
        re.search(
            r"(?mi)^[ \t]{0,3}>?[ \t]*#{1,6}[ \t]*"
            r"(?:review skipped|review limit reached|rate limit reached|"
            r"reviews? (?:are )?(?:disabled|blocked)|rate limited by coderabbit)\b",
            text,
        )
        or re.search(
            r"(?mi)^[ \t]{0,3}>[ \t]*"
            r"(?:auto reviews are disabled|reviews? (?:are )?(?:disabled|blocked))\b",
            text,
        )
        or re.match(
            r"(?i)^\s*(?:>\s*)?"
            r"(?:review skipped|review limit reached|rate limit reached|"
            r"rate limited by coderabbit|auto reviews are disabled|"
            r"reviews? (?:are )?(?:disabled|blocked))\b",
            text,
        )
    )


def fetch_coderabbit_sections(n: int) -> dict | None:
    """Fetch the Walkthrough/Changes sections from a CodeRabbit comment or review.

    Reviews normally contain an "Actionable comments posted" summary instead of
    those headings, so the oldest usable review body is used as a fallback.
    """
    # Check issue comments first (oldest first; API returns ascending ID order)
    comments = gh(f"repos/{REPO}/issues/{n}/comments?per_page=50")
    if isinstance(comments, list):
        for c in comments:
            if "coderabbit" in (c.get("user") or {}).get("login", "").lower() and c.get("body"):
                extracted = extract_walkthrough_and_changes(c["body"])
                if extracted:
                    return extracted

    # Fallback: PR reviews (oldest first; API returns chronological order).
    # CodeRabbit reviews usually have an "Actionable comments posted" summary
    # rather than Walkthrough/Changes headings, so keep the oldest usable body.
    reviews = gh(f"repos/{REPO}/pulls/{n}/reviews?per_page=50")
    review_fallback = None
    if isinstance(reviews, list):
        for r in reviews:
            login = (r.get("user") or {}).get("login", "").lower()
            body = (r.get("body") or "").strip()
            if "coderabbit" not in login or not body:
                continue
            extracted = extract_walkthrough_and_changes(body)
            if extracted:
                return extracted
            if review_fallback is None and not is_coderabbit_skip_or_blocked(body):
                review_fallback = {"walkthrough": body[:800], "changes": ""}

    if review_fallback:
        return review_fallback

    return None


def _extract_markdown_section(text: str, titles: tuple[str, ...]) -> str | None:
    """Extract a heading and its body, keeping child headings in the section.

    The section ends at the next heading of the same or higher level.
    """
    title_pattern = "|".join(re.escape(title) for title in titles)
    heading_re = re.compile(
        rf"^[ \t]{{0,3}}(#{{1,6}})[ \t]+(?:{title_pattern})\b[^\n]*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = heading_re.search(text)
    if not match:
        return None

    level = len(match.group(1))
    start = match.end()
    if start < len(text) and text[start] == "\n":
        start += 1

    fence = None
    offset = 0
    for line in text[start:].splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        elif fence is None:
            boundary = re.match(r"^[ \t]{0,3}(#{1,6})[ \t]+\S", line)
            if boundary and len(boundary.group(1)) <= level:
                return text[start:start + offset].strip()
        offset += len(line)

    return text[start:].strip()


def _has_coderabbit_review_content(text: str) -> bool:
    """Return True when text contains a non-empty walkthrough or changes section."""
    walkthrough = _extract_markdown_section(text, ("Walkthrough",))
    if walkthrough is None:
        walkthrough = _extract_markdown_section(
            text, ("Summary by CodeRabbit", "Summary", "Overview")
        )
    changes = _extract_markdown_section(text, ("Change", "Changes"))
    return bool(walkthrough or changes)


def extract_walkthrough_and_changes(text: str) -> dict | None:
    """Pull only the Walkthrough and Changes table from a CodeRabbit comment or review."""
    if not text or is_coderabbit_skip_or_blocked(text):
        return None

    result = {}

    walkthrough = _extract_markdown_section(text, ("Walkthrough",))
    if walkthrough is None:
        walkthrough = _extract_markdown_section(
            text, ("Summary by CodeRabbit", "Summary", "Overview")
        )
    if walkthrough:
        result["walkthrough"] = walkthrough

    changes = _extract_markdown_section(text, ("Change", "Changes"))
    if changes:
        result["changes"] = changes

    if not result:
        return None

    result.setdefault("walkthrough", "")
    result.setdefault("changes", "")
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
