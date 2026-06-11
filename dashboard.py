"""
MiniChain PR Dashboard
- Groups PRs by the PROBLEM they solve (not file overlap)
- Detects idea conflicts: same problem, different approach
- Generates rich HTML dashboards with full context for mentor

Run: python dashboard.py
Requires: gh (authenticated), ollama running on localhost:11434
"""

import subprocess, json, re, webbrowser, os, time
import urllib.request, urllib.error
from datetime import datetime
from collections import defaultdict

REPO         = "StabilityNexus/MiniChain"
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"
OUT_DIR      = os.path.dirname(os.path.abspath(__file__))

# ── gh helpers ────────────────────────────────────────────────────────────────

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

# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_prs():
    # TEST MODE: last 10 closed PRs. For production change to open
    prs = gh(f"repos/{REPO}/pulls?state=closed&per_page=10&sort=updated&direction=desc")
    return prs if isinstance(prs, list) else []
    # PRODUCTION:
    # return gh_paginate(f"repos/{REPO}/pulls?state=open&per_page=100")

def fetch_pr_files(n):
    files = gh(f"repos/{REPO}/pulls/{n}/files?per_page=100")
    return [f["filename"] for f in files] if isinstance(files, list) else []

def fetch_coderabbit(n):
    comments = gh(f"repos/{REPO}/issues/{n}/comments?per_page=50")
    if isinstance(comments, list):
        for c in comments:
            if "coderabbit" in c.get("user", {}).get("login", "").lower() and c.get("body"):
                return c["body"]
    reviews = gh(f"repos/{REPO}/pulls/{n}/reviews?per_page=50")
    if isinstance(reviews, list):
        for r in reviews:
            if "coderabbit" in r.get("user", {}).get("login", "").lower() and r.get("body"):
                return r["body"]
    return None

def extract_linked_issue(body):
    if not body:
        return None
    m = re.search(r"(?:fixes|closes|resolves)\s+#(\d+)", body, re.IGNORECASE)
    return int(m.group(1)) if m else None

# ── Ollama ────────────────────────────────────────────────────────────────────

def ollama(prompt):
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
    except Exception as e:
        print(f"    Ollama error: {e}")
        return None

def analyse_pr(pr):
    """Deep analysis of a single PR."""
    cr = (pr["coderabbit"] or "No CodeRabbit review available.")[:2500]
    files_str = ", ".join(pr["files"][:20]) or "unknown"

    prompt = f"""You are a senior code reviewer analysing a GitHub pull request for MiniChain — a minimal educational Python blockchain.

PR #{pr['number']}: {pr['title']}
Author: {pr['author']}
Files changed: {files_str}
PR description: {(pr.get('body') or 'none')[:500]}
CodeRabbit review:
{cr}

Reply ONLY with a JSON object, no markdown, no explanation:
{{
  "problem": "the specific problem this PR is trying to solve in 1 sentence (be precise, e.g. 'blockchain state is lost on node restart' not 'persistence')",
  "problem_category": "one of: persistence, mempool, networking, validation, cli, testing, refactor, security, other",
  "approach": "how this PR solves the problem in 2-3 sentences. Be specific about the technical method used.",
  "what_changed": "bullet list of the 3-5 most important code changes as a single string separated by |",
  "strengths": "what this approach does well in 1-2 sentences",
  "weaknesses": "what this approach does poorly or leaves unresolved in 1-2 sentences",
  "outcome_if_merged": "what the codebase state will be after this PR is merged, 1-2 sentences",
  "open_questions": "questions mentor should ask before merging, as a single string separated by |",
  "risk": "low or medium or high",
  "summary": "one sentence TL;DR"
}}"""

    result = ollama(prompt)
    if not result:
        return {
            "problem": pr["title"],
            "problem_category": "other",
            "approach": "Could not analyse.",
            "what_changed": pr["title"],
            "strengths": "Unknown",
            "weaknesses": "Unknown",
            "outcome_if_merged": "Unknown",
            "open_questions": "",
            "risk": "medium",
            "summary": pr["title"]
        }
    return result

def compare_prs(pr_a, pr_b):
    """Ask Ollama to compare two PRs solving the same problem."""
    prompt = f"""Two pull requests are solving the same problem in MiniChain (a minimal Python blockchain).
Compare them and give mentor a clear recommendation.

PR #{pr_a['number']} by {pr_a['author']}:
Problem: {pr_a['analysis']['problem']}
Approach: {pr_a['analysis']['approach']}
Strengths: {pr_a['analysis']['strengths']}
Weaknesses: {pr_a['analysis']['weaknesses']}

PR #{pr_b['number']} by {pr_b['author']}:
Problem: {pr_b['analysis']['problem']}
Approach: {pr_b['analysis']['approach']}
Strengths: {pr_b['analysis']['strengths']}
Weaknesses: {pr_b['analysis']['weaknesses']}

Reply ONLY with a JSON object, no markdown:
{{
  "why_they_conflict": "explain clearly why these two approaches conflict or overlap in 2-3 sentences",
  "shared_goal": "what both PRs are ultimately trying to achieve — where they agree",
  "if_merge_a_first": "what happens to the codebase if #{pr_a['number']} is merged first, in 2 sentences",
  "if_merge_b_first": "what happens to the codebase if #{pr_b['number']} is merged first, in 2 sentences",
  "if_merge_both": "what happens if both are merged (conflicts, redundancy, benefit), 2 sentences",
  "recommendation": "which PR mentor should prefer and why, or how to combine them, 2-3 sentences",
  "preferred_pr": "{pr_a['number']} or {pr_b['number']} or both or neither"
}}"""

    result = ollama(prompt)
    if not result:
        return {
            "why_they_conflict": "Could not analyse.",
            "shared_goal": "Unknown",
            "if_merge_a_first": "Unknown",
            "if_merge_b_first": "Unknown",
            "if_merge_both": "Unknown",
            "recommendation": "Manual review required.",
            "preferred_pr": "neither"
        }
    return result

# ── Grouping by problem ───────────────────────────────────────────────────────

def group_by_problem(pr_data):
    """
    Group PRs by problem_category first, then use Ollama to check
    if PRs in the same category are actually solving the same problem.
    Returns: conflict_groups, isolated
    """
    by_category = defaultdict(list)
    for pr in pr_data:
        cat = pr["analysis"]["problem_category"]
        by_category[cat].append(pr)

    conflict_groups = []
    isolated = []

    for cat, prs in by_category.items():
        if len(prs) == 1:
            isolated.append(prs[0])
            continue

        # Multiple PRs in same category — check pairwise if same problem
        used = set()
        for i in range(len(prs)):
            if prs[i]["number"] in used:
                continue
            group = [prs[i]]
            for j in range(i+1, len(prs)):
                if prs[j]["number"] in used:
                    continue
                # Quick heuristic: if problem text overlap is high, same problem
                prob_a = prs[i]["analysis"]["problem"].lower()
                prob_b = prs[j]["analysis"]["problem"].lower()
                words_a = set(prob_a.split())
                words_b = set(prob_b.split())
                overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
                if overlap > 0.25:  # 25% word overlap = same problem
                    group.append(prs[j])
                    used.add(prs[j]["number"])
            used.add(prs[i]["number"])

            if len(group) > 1:
                # Run pairwise comparisons
                comparisons = []
                for x in range(len(group)):
                    for y in range(x+1, len(group)):
                        print(f"    Comparing PR #{group[x]['number']} vs #{group[y]['number']}...")
                        comp = compare_prs(group[x], group[y])
                        comparisons.append({
                            "pr_a": group[x],
                            "pr_b": group[y],
                            "analysis": comp
                        })
                conflict_groups.append({
                    "category": cat,
                    "prs": group,
                    "comparisons": comparisons
                })
            else:
                isolated.append(group[0])

    return conflict_groups, isolated

# ── HTML helpers ──────────────────────────────────────────────────────────────

RISK_COLOR = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}
RISK_BG    = {"low": "#f0fdf4", "medium": "#fffbeb", "high": "#fef2f2"}

def e(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def risk_badge(risk):
    c = RISK_COLOR.get(risk, "#888")
    return f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{risk.capitalize()} Risk</span>'

def bullet_list(text, color="#374151"):
    if not text:
        return ""
    items = [t.strip() for t in text.split("|") if t.strip()]
    return "<ul style='margin:6px 0 6px 16px;'>" + "".join(
        f'<li style="font-size:13px;color:{color};margin-bottom:3px">{e(item)}</li>'
        for item in items
    ) + "</ul>"

def md_to_html(text):
    if not text:
        return "<em style='color:#9ca3af'>No CodeRabbit review found.</em>"
    text = text[:2500] + ("..." if len(text) > 2500 else "")
    text = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*",     r"<em>\1</em>",         text)
    text = re.sub(r"`(.*?)`",       r"<code>\1</code>",     text)
    text = re.sub(r"^#{1,3} (.+)$", r"<h4 style='margin:10px 0 4px;font-size:13px'>\1</h4>", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "</p><p style='margin-bottom:8px'>", text)
    return f"<p style='margin-bottom:8px'>{text}</p>"

def pr_detail_block(pr, highlight_color="#1d4ed8"):
    a = pr["analysis"]
    files_html = "".join(
        f'<span style="background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;font-family:monospace">{f}</span>'
        for f in pr["files"][:12]
    ) + (f'<span style="font-size:11px;color:#6b7280"> +{len(pr["files"])-12} more</span>' if len(pr["files"]) > 12 else "")

    return f"""
    <div style="border:2px solid {highlight_color};border-radius:10px;padding:18px;background:#fff">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px">
            <a href="https://github.com/{REPO}/pull/{pr['number']}" target="_blank"
               style="font-size:15px;font-weight:800;color:{highlight_color};text-decoration:none">
                PR #{pr['number']} &mdash; {e(pr['title'])}
            </a>
            {risk_badge(a.get('risk','medium'))}
        </div>
        <div style="font-size:12px;color:#6b7280;margin-bottom:12px">
            &#128100; <strong>{e(pr['author'])}</strong> &middot; {pr['created_at'][:10]}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
            <div style="background:#f9fafb;border-radius:8px;padding:12px">
                <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">Problem Being Solved</div>
                <div style="font-size:13px;color:#111">{e(a.get('problem',''))}</div>
            </div>
            <div style="background:#f9fafb;border-radius:8px;padding:12px">
                <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">Approach</div>
                <div style="font-size:13px;color:#111">{e(a.get('approach',''))}</div>
            </div>
        </div>

        <div style="margin-bottom:10px">
            <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">What Changed</div>
            {bullet_list(a.get('what_changed',''))}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
            <div style="background:#f0fdf4;border-radius:8px;padding:10px">
                <div style="font-size:11px;font-weight:700;color:#15803d;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">&#10003; Strengths</div>
                <div style="font-size:13px;color:#374151">{e(a.get('strengths',''))}</div>
            </div>
            <div style="background:#fef2f2;border-radius:8px;padding:10px">
                <div style="font-size:11px;font-weight:700;color:#dc2626;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">&#10007; Weaknesses</div>
                <div style="font-size:13px;color:#374151">{e(a.get('weaknesses',''))}</div>
            </div>
        </div>

        <div style="background:#eff6ff;border-radius:8px;padding:10px;margin-bottom:12px">
            <div style="font-size:11px;font-weight:700;color:#1d4ed8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">&#128269; Outcome If Merged</div>
            <div style="font-size:13px;color:#1e3a5f">{e(a.get('outcome_if_merged',''))}</div>
        </div>

        <div style="margin-bottom:12px">
            <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">&#10067; Open Questions for mentor</div>
            {bullet_list(a.get('open_questions',''), '#92400e') if a.get('open_questions') else '<div style="font-size:13px;color:#9ca3af">None flagged.</div>'}
        </div>

        <div style="margin-bottom:10px">{files_html}</div>

        <details style="margin-top:10px">
            <summary style="cursor:pointer;font-size:12px;font-weight:600;color:#6b7280">&#128048; CodeRabbit Full Review</summary>
            <div style="margin-top:10px;font-size:13px;line-height:1.7;max-height:320px;overflow-y:auto;
                        border:1px solid #e5e7eb;border-radius:6px;padding:12px;color:#374151">
                {md_to_html(pr['coderabbit'])}
            </div>
        </details>
    </div>"""

# ── Conflict tree HTML ────────────────────────────────────────────────────────

def build_conflict_html(groups):
    now = datetime.now().strftime("%d %b %Y %H:%M")
    sections = []

    for gi, group in enumerate(groups):
        cat   = group["category"].replace("_"," ").title()
        prs   = group["prs"]
        comps = group["comparisons"]

        pr_colors = ["#1d4ed8", "#dc2626", "#7c3aed", "#047857"]

        # SVG tree
        n_prs    = len(prs)
        ROOT_X   = 100
        ROOT_Y   = 80
        BRANCH_X = 300
        LEAF_X   = 520
        END_X    = 700
        NODE_R   = 28
        V_GAP    = 130
        SVG_H    = max(280, n_prs * V_GAP + 80)
        SVG_W    = 820

        start_y  = (SVG_H - (n_prs - 1) * V_GAP) // 2
        ys       = [start_y + i * V_GAP for i in range(n_prs)]
        root_y   = SVG_H // 2

        svg = [f"""<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:{SVG_W}px;background:#0d1117;border-radius:12px">
  <defs>"""]
        for ci, col in enumerate(pr_colors[:n_prs]):
            svg.append(f'<marker id="arr{gi}{ci}" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="{col}"/></marker>')
        svg.append("</defs>")

        # Root node
        svg.append(f"""
  <circle cx="{ROOT_X}" cy="{root_y}" r="{NODE_R+4}" fill="#1f6feb" stroke="#388bfd" stroke-width="2"/>
  <text x="{ROOT_X}" y="{root_y-5}" text-anchor="middle" font-size="11" fill="white" font-weight="700">main</text>
  <text x="{ROOT_X}" y="{root_y+9}" text-anchor="middle" font-size="9" fill="#93c5fd">current</text>""")

        # Each PR branch
        for i, (pr, y) in enumerate(zip(prs, ys)):
            col   = pr_colors[i % len(pr_colors)]
            risk  = pr["analysis"].get("risk","medium")
            rc    = RISK_COLOR.get(risk,"#888")
            summ  = e(pr["analysis"]["summary"][:42])
            outc  = e(pr["analysis"]["outcome_if_merged"][:48])

            # root → branch arrow
            svg.append(f"""
  <path d="M{ROOT_X+NODE_R+4},{root_y} Q{(ROOT_X+BRANCH_X)//2},{y} {BRANCH_X-NODE_R},{y}"
        fill="none" stroke="{col}" stroke-width="1.8" marker-end="url(#arr{gi}{i})"/>
  <!-- PR node -->
  <circle cx="{BRANCH_X}" cy="{y}" r="{NODE_R}" fill="#161b22" stroke="{col}" stroke-width="2.5"/>
  <text x="{BRANCH_X}" y="{y-7}" text-anchor="middle" font-size="11" fill="{col}" font-weight="800">#{pr['number']}</text>
  <text x="{BRANCH_X}" y="{y+7}" text-anchor="middle" font-size="9" fill="#8b949e">{e(pr['author'])}</text>
  <!-- Summary label -->
  <rect x="{BRANCH_X+NODE_R+6}" y="{y-18}" width="175" height="36" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="{BRANCH_X+NODE_R+10}" y="{y-4}" font-size="8.5" fill="#e6edf3">{summ}</text>
  <text x="{BRANCH_X+NODE_R+10}" y="{y+12}" font-size="8" fill="{rc}">Risk: {risk}</text>
  <!-- branch → outcome arrow -->
  <line x1="{LEAF_X-5}" y1="{y}" x2="{END_X-NODE_R-4}" y2="{y}"
        stroke="{col}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr{gi}{i})"/>
  <!-- Outcome node -->
  <circle cx="{END_X}" cy="{y}" r="{NODE_R-4}" fill="#1f2937" stroke="{col}" stroke-width="2"/>
  <text x="{END_X}" y="{y-4}" text-anchor="middle" font-size="8" fill="{col}" font-weight="700">after</text>
  <text x="{END_X}" y="{y+8}" text-anchor="middle" font-size="8" fill="{col}">merge</text>
  <!-- Outcome tooltip -->
  <rect x="{END_X+NODE_R-2}" y="{y-18}" width="200" height="36" rx="4" fill="#1f2937" stroke="{col}" stroke-opacity="0.4"/>
  <text x="{END_X+NODE_R+2}" y="{y-4}" font-size="7.5" fill="#c9d1d9">{outc[:48]}</text>
  <text x="{END_X+NODE_R+2}" y="{y+10}" font-size="7.5" fill="#c9d1d9">{outc[48:96]}</text>""")

        svg.append("</svg>")
        svg_html = "\n".join(svg)

        # Comparison cards
        comp_cards = ""
        for comp in comps:
            ca  = comp["analysis"]
            a   = comp["pr_a"]
            b   = comp["pr_b"]
            pref = str(ca.get("preferred_pr","neither"))
            pref_label = f"PR #{pref}" if pref not in ("both","neither") else pref.capitalize()
            pref_color = "#22c55e" if pref not in ("neither",) else "#f59e0b"

            comp_cards += f"""
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-top:16px">
                <div style="font-size:14px;font-weight:800;color:#111;margin-bottom:14px">
                    PR #{a['number']} vs PR #{b['number']} &mdash; Head-to-Head
                </div>

                <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px;border-radius:0 8px 8px 0;margin-bottom:14px">
                    <div style="font-size:11px;font-weight:700;color:#92400e;text-transform:uppercase;margin-bottom:4px">Why They Conflict</div>
                    <div style="font-size:13px;color:#78350f">{e(ca.get('why_they_conflict',''))}</div>
                </div>

                <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:12px;border-radius:0 8px 8px 0;margin-bottom:14px">
                    <div style="font-size:11px;font-weight:700;color:#15803d;text-transform:uppercase;margin-bottom:4px">Shared Goal — Where They Meet</div>
                    <div style="font-size:13px;color:#166534">{e(ca.get('shared_goal',''))}</div>
                </div>

                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
                    <div style="background:#eff6ff;border-radius:8px;padding:12px">
                        <div style="font-size:11px;font-weight:700;color:#1d4ed8;text-transform:uppercase;margin-bottom:4px">If #{a['number']} merged first</div>
                        <div style="font-size:12px;color:#1e3a5f">{e(ca.get('if_merge_a_first',''))}</div>
                    </div>
                    <div style="background:#fef2f2;border-radius:8px;padding:12px">
                        <div style="font-size:11px;font-weight:700;color:#dc2626;text-transform:uppercase;margin-bottom:4px">If #{b['number']} merged first</div>
                        <div style="font-size:12px;color:#7f1d1d">{e(ca.get('if_merge_b_first',''))}</div>
                    </div>
                    <div style="background:#f5f3ff;border-radius:8px;padding:12px">
                        <div style="font-size:11px;font-weight:700;color:#7c3aed;text-transform:uppercase;margin-bottom:4px">If both merged</div>
                        <div style="font-size:12px;color:#4c1d95">{e(ca.get('if_merge_both',''))}</div>
                    </div>
                </div>

                <div style="background:#111827;border-radius:8px;padding:14px">
                    <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:6px">&#129302; Recommendation</div>
                    <div style="font-size:13px;color:#e5e7eb;line-height:1.6">{e(ca.get('recommendation',''))}</div>
                    <div style="margin-top:8px">
                        <span style="background:{pref_color};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700">
                            Prefer: {pref_label}
                        </span>
                    </div>
                </div>
            </div>"""

        # Full PR detail blocks side by side
        pr_details = ""
        for i, pr in enumerate(prs):
            col = pr_colors[i % len(pr_colors)]
            pr_details += f'<div style="flex:1;min-width:340px">{pr_detail_block(pr, col)}</div>'

        sections.append(f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;margin-bottom:32px;box-shadow:0 2px 8px rgba(0,0,0,.06)">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="background:#dc2626;color:#fff;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:700">IDEA CONFLICT</span>
                <span style="background:#f3f4f6;color:#374151;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:600">Category: {cat}</span>
                <span style="font-size:13px;color:#6b7280">{len(prs)} PRs solving the same problem differently</span>
            </div>
            <div style="font-size:13px;color:#374151;margin-bottom:16px;padding:10px;background:#fffbeb;border-radius:6px;border-left:3px solid #f59e0b">
                <strong>Shared problem:</strong> {e(prs[0]['analysis']['problem'])}
            </div>
            {svg_html}
            {comp_cards}
            <div style="margin-top:20px">
                <div style="font-size:13px;font-weight:700;color:#374151;margin-bottom:12px">Full PR Details</div>
                <div style="display:flex;gap:16px;flex-wrap:wrap">{pr_details}</div>
            </div>
        </div>""")

    body = "\n".join(sections) if sections else '<p style="color:#6b7280;padding:20px;text-align:center">No idea conflicts detected.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PR Idea Conflicts — MiniChain</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f3f4f6;color:#111;padding:24px}}
  h1{{font-size:22px;font-weight:800;margin-bottom:4px}}
  .sub{{font-size:13px;color:#6b7280;margin-bottom:28px}}
  code{{font-family:monospace;background:#f3f4f6;padding:1px 5px;border-radius:3px}}
  a{{color:#1d4ed8}}
  h4{{color:#374151}}
</style>
</head>
<body>
<h1>&#9889; PR Idea Conflict Analysis</h1>
<p class="sub">{REPO} &middot; {now} &middot; {len(groups)} conflict group(s) &middot; Powered by Ollama {OLLAMA_MODEL}</p>
{body}
</body>
</html>"""

# ── Isolated HTML ─────────────────────────────────────────────────────────────

def build_isolated_html(isolated):
    now = datetime.now().strftime("%d %b %Y %H:%M")

    cards = ""
    for pr in sorted(isolated, key=lambda x: x["created_at"]):
        cards += f"""
        <div style="margin-bottom:20px">
            {pr_detail_block(pr, "#1d4ed8")}
        </div>"""

    empty = '<p style="color:#6b7280;padding:40px;text-align:center;font-size:14px">No isolated PRs — all PRs have idea overlaps.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Isolated PRs — MiniChain</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f3f4f6;color:#111;padding:24px}}
  h1{{font-size:22px;font-weight:800;margin-bottom:4px}}
  .sub{{font-size:13px;color:#6b7280;margin-bottom:28px}}
  code{{font-family:monospace;background:#f3f4f6;padding:1px 5px;border-radius:3px}}
  a{{color:#1d4ed8}}
  h4{{color:#374151}}
</style>
</head>
<body>
<h1>&#9989; Isolated PRs — Unique Problems, No Conflicts</h1>
<p class="sub">{REPO} &middot; {now} &middot; {len(isolated)} PR(s) solving unique problems</p>
{cards if cards else empty}
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    check = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if check.returncode != 0:
        print("ERROR: gh not authenticated. Run: gh auth login")
        return

    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
    except Exception:
        print("ERROR: Ollama not reachable at localhost:11434")
        return

    print(f"Fetching PRs for {REPO}...")
    raw_prs = fetch_prs()
    if not raw_prs:
        print("No PRs found.")
        return

    print(f"Found {len(raw_prs)} PRs. Running deep Ollama analysis (this takes a minute)...")
    pr_data = []
    for raw in raw_prs:
        num    = raw["number"]
        author = raw["user"]["login"]
        body   = raw.get("body", "") or ""
        print(f"\n  PR #{num} — {raw['title'][:55]}")

        pr = {
            "number":     num,
            "title":      raw["title"],
            "author":     author,
            "created_at": raw["created_at"],
            "body":       body,
            "files":      fetch_pr_files(num),
            "coderabbit": fetch_coderabbit(num),
        }
        print(f"    Analysing with Ollama...")
        pr["analysis"] = analyse_pr(pr)
        print(f"    Problem:  {pr['analysis']['problem'][:65]}")
        print(f"    Category: {pr['analysis']['problem_category']}")
        print(f"    Approach: {pr['analysis']['approach'][:65]}")
        pr_data.append(pr)

    print(f"\nGrouping by problem and running comparisons...")
    groups, isolated = group_by_problem(pr_data)

    print(f"\n  Conflict groups : {len(groups)}")
    print(f"  Isolated PRs    : {len(isolated)}")

    tree_path = os.path.join(OUT_DIR, "conflicts_tree.html")
    iso_path  = os.path.join(OUT_DIR, "isolated_prs.html")

    with open(tree_path, "w", encoding="utf-8") as f:
        f.write(build_conflict_html(groups))
    with open(iso_path, "w", encoding="utf-8") as f:
        f.write(build_isolated_html(isolated))

    print(f"\nOpening conflict tree  -> {tree_path}")
    webbrowser.open(f"file:///{tree_path}")
    time.sleep(1)
    print(f"Opening isolated PRs   -> {iso_path}")
    webbrowser.open(f"file:///{iso_path}")
    print("\nDone.")

if __name__ == "__main__":
    main()