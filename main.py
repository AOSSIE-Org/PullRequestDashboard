"""
main.py — entry point

Flow:
  1. Load context.md (repo context — what MiniChain is, what's already built)
  2. Fetch all PRs + extract CodeRabbit walkthrough + changes only
  3. One combined Ollama call → groups PRs by problem
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
    pr_data = []
    for raw in raw_prs:
        num    = raw["number"]
        author = raw["user"]["login"]
        print(f"  PR #{num} — {raw['title'][:55]}")
        pr_data.append({
            "number":     num,
            "title":      raw["title"],
            "author":     author,
            "created_at": raw["created_at"],
            "body":       raw.get("body", "") or "",
            "files":      fetch_pr_files(num),
            "coderabbit": fetch_coderabbit_sections(num),
        })

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