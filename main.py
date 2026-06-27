"""
main.py — entry point

Flow:
  1. Load context.md (repo context — what MiniChain is, what's already built)
  2. Fetch all PRs + extract CodeRabbit walkthrough + changes only
  3. One combined Ollama call -> groups PRs by problem
  4. Deep Ollama analysis per conflict group (all PRs in group together)
  5. Single Ollama analysis per isolated PR
  6. Render two HTML files and open in browser

Run: python main.py
Requires: gh (authenticated), ollama running on localhost:11434
Optional: context.md in same folder (drop it in when ready)
"""

import os, time, webbrowser
from github   import fetch_prs, fetch_pr_files, fetch_coderabbit_sections, check_gh_auth, REPO
from ollama   import check_ollama
from grouping import resolve_groups
from render   import build_conflict_html, build_isolated_html

OUT_DIR      = os.path.dirname(os.path.abspath(__file__))
CONTEXT_FILE = os.path.join(OUT_DIR, "context.md")


def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        print(f"  Loaded context.md ({len(content)} chars)")
        return content
    print("  No context.md found — running without repo context")
    print("  (Drop context.md in the same folder to enable it)")
    return ""


def _build_fallback_pr(raw):
    """Build a minimal PR dict when fetching fails — keeps the pipeline alive."""
    num = raw.get("number", 0)
    return {
        "number":     num,
        "title":      raw.get("title", f"PR #{num}"),
        "author":     raw.get("user", {}).get("login", "unknown"),
        "created_at": raw.get("created_at", ""),
        "body":       raw.get("body", "") or "",
        "files":      [],
        "coderabbit": None,
    }


def _build_pr_data(raw):
    """Fetch full data for one PR. Returns dict or raises on complete failure."""
    num    = raw["number"]
    author = raw["user"]["login"]
    title  = raw.get("title", "")[:55]

    files_error = False
    cr_error    = False

    try:
        files = fetch_pr_files(num)
    except Exception:
        files = []
        files_error = True

    try:
        coderabbit = fetch_coderabbit_sections(num)
    except Exception:
        coderabbit = None
        cr_error = True

    if files_error or cr_error:
        diagnostics = []
        if files_error:
            diagnostics.append("file fetch failed")
        if cr_error:
            diagnostics.append("CodeRabbit fetch failed")
        print(f"  WARNING PR #{num}: {', '.join(diagnostics)} — using partial data")

    return {
        "number":     num,
        "title":      raw.get("title", ""),
        "author":     author,
        "created_at": raw.get("created_at", ""),
        "body":       raw.get("body", "") or "",
        "files":      files,
        "coderabbit": coderabbit,
        "_incomplete": files_error or cr_error,
    }


def main():
    if not check_gh_auth():
        print("ERROR: gh not authenticated. Run: gh auth login")
        return

    if not check_ollama():
        print("ERROR: Ollama not reachable at localhost:11434")
        return

    print(f"\nLoading repo context...")
    repo_context = load_context()

    print(f"\nFetching PRs for {REPO}...")
    raw_prs = fetch_prs()
    if not raw_prs:
        print("No PRs found.")
        return

    print(f"Found {len(raw_prs)} PRs. Fetching walkthroughs...\n")

    # Per-PR error isolation: a single failing PR won't kill the whole run
    pr_data = []
    failed = 0
    for raw in raw_prs:
        num = raw["number"]
        print(f"  PR #{num} — {raw.get('title', '')[:55]}")
        try:
            pr = _build_pr_data(raw)
            pr_data.append(pr)
            if pr.get("_incomplete"):
                failed += 1
        except Exception as e:
            print(f"  ERROR PR #{num}: {e} — using fallback placeholder")
            pr_data.append(_build_fallback_pr(raw))
            failed += 1

    if failed:
        print(f"\n  {failed} PR(s) had fetch errors — results may be incomplete")

    if not pr_data:
        print("No PR data to analyse.")
        return

    # ── Step 2: Semantic clustering + deep analysis ──────────────────────────
    print(f"\nClustering {len(pr_data)} PRs by semantic similarity...")
    conflict_groups, isolated = resolve_groups(pr_data, repo_context)

    print(f"\n  Conflict groups : {len(conflict_groups)}")
    print(f"  Isolated PRs    : {len(isolated)}")

    # ── Render ────────────────────────────────────────────────────────────────
    tree_path = os.path.join(OUT_DIR, "conflicts_tree.html")
    iso_path  = os.path.join(OUT_DIR, "isolated_prs.html")

    with open(tree_path, "w", encoding="utf-8") as f:
        f.write(build_conflict_html(conflict_groups))
    with open(iso_path, "w", encoding="utf-8") as f:
        f.write(build_isolated_html(isolated))

    print(f"\nOpening conflict tree -> {tree_path}")
    webbrowser.open(f"file:///{tree_path}")
    time.sleep(1)
    print(f"Opening isolated PRs  -> {iso_path}")
    webbrowser.open(f"file:///{iso_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
