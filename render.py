"""
render.py — builds conflict_tree.html and isolated_prs.html
"""

import re
from datetime import datetime
from github import REPO

RISK_COLOR = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}
PR_COLORS  = ["#1d4ed8", "#dc2626", "#7c3aed", "#047857", "#b45309"]

# ── Shared utils ──────────────────────────────────────────────────────────────

def e(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

def risk_badge(risk):
    c = RISK_COLOR.get(risk, "#888")
    return f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{risk.capitalize()} Risk</span>'

def bullet_list(text, color="#374151"):
    if not text:
        return ""
    items = [t.strip() for t in text.split("|") if t.strip()]
    return "<ul style='margin:6px 0 6px 18px'>" + "".join(
        f'<li style="font-size:13px;color:{color};margin-bottom:3px">{e(item)}</li>'
        for item in items
    ) + "</ul>"

def cr_to_html(cr):
    """Render only walkthrough + changes from the extracted CR dict."""
    if not cr:
        return "<em style='color:#9ca3af'>No CodeRabbit review found.</em>"

    parts = []
    if cr.get("walkthrough"):
        wt = cr["walkthrough"]
        wt = wt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        wt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", wt)
        wt = re.sub(r"`(.*?)`",       r"<code>\1</code>",     wt)
        wt = re.sub(r"\n{2,}", "</p><p style='margin-bottom:6px'>", wt)
        parts.append(f"<p style='font-weight:700;color:#374151;margin-bottom:6px'>Walkthrough</p><p style='margin-bottom:6px'>{wt}</p>")

    if cr.get("changes"):
        ch = cr["changes"]
        ch = ch.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        # Render markdown table as-is in a pre block
        parts.append(f"<p style='font-weight:700;color:#374151;margin:10px 0 6px'>Changes</p><pre style='font-size:11px;white-space:pre-wrap;color:#374151;background:#f9fafb;padding:10px;border-radius:6px'>{ch}</pre>")

    return "\n".join(parts)

def pr_detail_block(pr, color="#1d4ed8"):
    a         = pr["analysis"]
    files_html = "".join(
        f'<span style="background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:11px;margin:2px;display:inline-block;font-family:monospace">{f}</span>'
        for f in pr["files"][:12]
    ) + (f'<span style="font-size:11px;color:#6b7280"> +{len(pr["files"])-12} more</span>' if len(pr["files"]) > 12 else "")

    return f"""
    <div style="border:2px solid {color};border-radius:10px;padding:18px;background:#fff">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px">
            <a href="https://github.com/{REPO}/pull/{pr['number']}" target="_blank"
               style="font-size:15px;font-weight:800;color:{color};text-decoration:none">
                PR #{pr['number']} &mdash; {e(pr['title'])}
            </a>
            {risk_badge(a.get('risk','medium'))}
        </div>
        <div style="font-size:12px;color:#6b7280;margin-bottom:12px">
            &#128100; <strong>{e(pr['author'])}</strong> &middot; {pr['created_at'][:10]}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
            <div style="background:#f9fafb;border-radius:8px;padding:12px">
                <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:5px">Problem</div>
                <div style="font-size:13px;color:#111">{e(a.get('problem',''))}</div>
            </div>
            <div style="background:#f9fafb;border-radius:8px;padding:12px">
                <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:5px">Approach</div>
                <div style="font-size:13px;color:#111">{e(a.get('approach',''))}</div>
            </div>
        </div>

        <div style="margin-bottom:10px">
            <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:4px">What Changed</div>
            {bullet_list(a.get('what_changed',''))}
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
            <div style="background:#f0fdf4;border-radius:8px;padding:10px">
                <div style="font-size:11px;font-weight:700;color:#15803d;text-transform:uppercase;margin-bottom:4px">&#10003; Strengths</div>
                <div style="font-size:13px;color:#374151">{e(a.get('strengths',''))}</div>
            </div>
            <div style="background:#fef2f2;border-radius:8px;padding:10px">
                <div style="font-size:11px;font-weight:700;color:#dc2626;text-transform:uppercase;margin-bottom:4px">&#10007; Weaknesses</div>
                <div style="font-size:13px;color:#374151">{e(a.get('weaknesses',''))}</div>
            </div>
        </div>

        <div style="background:#eff6ff;border-radius:8px;padding:10px;margin-bottom:10px">
            <div style="font-size:11px;font-weight:700;color:#1d4ed8;text-transform:uppercase;margin-bottom:4px">&#128269; Outcome If Merged</div>
            <div style="font-size:13px;color:#1e3a5f">{e(a.get('outcome_if_merged',''))}</div>
        </div>

        <div style="margin-bottom:10px">
            <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:4px">&#10067; Open Questions for mentor</div>
            {bullet_list(a.get('open_questions',''), '#92400e') if a.get('open_questions') else '<div style="font-size:13px;color:#9ca3af">None flagged.</div>'}
        </div>

        <div style="margin-bottom:10px">{files_html}</div>

        <details style="margin-top:10px">
            <summary style="cursor:pointer;font-size:12px;font-weight:600;color:#6b7280">&#128048; CodeRabbit Walkthrough &amp; Changes</summary>
            <div style="margin-top:10px;font-size:13px;line-height:1.7;max-height:360px;overflow-y:auto;
                        border:1px solid #e5e7eb;border-radius:6px;padding:14px;color:#374151">
                {cr_to_html(pr.get('coderabbit'))}
            </div>
        </details>
    </div>"""

# ── SVG DAG tree ─────────────────────────────────────────────────────────────
# Proper merge graph:
#   DUPLICATE  → branches converge to ONE shared outcome node
#   CONFLICT   → separate outcome nodes + "if both merged" convergence node
#   All nodes  → root (main) branches out, outcomes show right side

def _svg_tree(group, gi):
    prs      = group["prs"]
    ga       = group.get("analysis") or {}
    n        = len(prs)
    gtype    = group.get("group_type", "conflict")  # "duplicate" or "conflict"

    # Layout
    RX       = 80
    BX       = 260
    OX       = 480
    MX       = 660   # merge/convergence node X
    NR       = 24
    GAP      = 140
    SVG_H    = max(280, n * GAP + 100)
    SVG_W    = 900
    root_y   = SVG_H // 2
    start_y  = (SVG_H - (n - 1) * GAP) // 2
    ys       = [start_y + i * GAP for i in range(n)]

    markers = "".join(
        f'<marker id="a{gi}{i}" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="{PR_COLORS[i % len(PR_COLORS)]}"/></marker>'
        for i in range(n)
    )
    markers += f'<marker id="am{gi}" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#8b5cf6"/></marker>'

    svg = [f'''<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg"
     style="width:100%;max-width:{SVG_W}px;background:#0d1117;border-radius:12px;margin-bottom:8px">
  <defs>{markers}</defs>''']

    # Root node (main)
    svg.append(f'''
  <circle cx="{RX}" cy="{root_y}" r="{NR+5}" fill="#1f6feb" stroke="#388bfd" stroke-width="2.5"/>
  <text x="{RX}" y="{root_y-5}" text-anchor="middle" font-size="12" fill="white" font-weight="800">main</text>
  <text x="{RX}" y="{root_y+9}" text-anchor="middle" font-size="9" fill="#93c5fd">current</text>''')

    # Type label top-right
    type_color = "#8b5cf6" if gtype == "duplicate" else "#ef4444"
    type_label = "DUPLICATE" if gtype == "duplicate" else "CONFLICT"
    svg.append(f'<rect x="{SVG_W-110}" y="10" width="100" height="22" rx="6" fill="{type_color}" opacity="0.2"/>')
    svg.append(f'<text x="{SVG_W-60}" y="25" text-anchor="middle" font-size="11" font-weight="700" fill="{type_color}">{type_label}</text>')

    if gtype == "duplicate":
        # All branches converge to ONE shared outcome node at center-right
        conv_y   = root_y
        conv_x   = OX

        for i, (pr, y) in enumerate(zip(prs, ys)):
            col  = PR_COLORS[i % len(PR_COLORS)]
            risk = pr.get("analysis", {}).get("risk", "medium")
            rc   = RISK_COLOR.get(risk, "#888")
            summ = e(pr.get("analysis", {}).get("summary", pr["title"])[:40])

            # root → PR node
            svg.append(f'''
  <path d="M{RX+NR+5},{root_y} Q{(RX+BX)//2},{y} {BX-NR},{y}"
        fill="none" stroke="{col}" stroke-width="1.8" marker-end="url(#a{gi}{i})"/>
  <circle cx="{BX}" cy="{y}" r="{NR}" fill="#161b22" stroke="{col}" stroke-width="2.5"/>
  <text x="{BX}" y="{y-7}" text-anchor="middle" font-size="11" fill="{col}" font-weight="800">#{pr["number"]}</text>
  <text x="{BX}" y="{y+7}" text-anchor="middle" font-size="9" fill="#8b949e">{e(pr["author"])}</text>
  <rect x="{BX+NR+4}" y="{y-14}" width="160" height="28" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="{BX+NR+8}" y="{y}" font-size="8" fill="#e6edf3">{summ}</text>
  <text x="{BX+NR+8}" y="{y+12}" font-size="7.5" fill="{rc}">Risk: {risk}</text>''')

            # PR node → shared convergence node
            svg.append(f'''
  <path d="M{BX+NR+168},{y} Q{(BX+conv_x)//2+30},{(y+conv_y)//2} {conv_x-NR-4},{conv_y}"
        fill="none" stroke="{col}" stroke-width="1.5" stroke-dasharray="6,3" marker-end="url(#a{gi}{i})"/>''')

        # Shared outcome node — bigger, purple
        outc = e(ga.get("shared_problem", "Same outcome")[:55])
        svg.append(f'''
  <circle cx="{conv_x}" cy="{conv_y}" r="{NR+10}" fill="#1f1035" stroke="#8b5cf6" stroke-width="3"/>
  <text x="{conv_x}" y="{conv_y-8}" text-anchor="middle" font-size="10" fill="#8b5cf6" font-weight="800">SAME</text>
  <text x="{conv_x}" y="{conv_y+6}" text-anchor="middle" font-size="9" fill="#c4b5fd">OUTCOME</text>
  <rect x="{conv_x+NR+12}" y="{conv_y-20}" width="200" height="40" rx="6" fill="#1f1035" stroke="#8b5cf6" stroke-opacity="0.5"/>
  <text x="{conv_x+NR+16}" y="{conv_y-5}" font-size="8" fill="#c4b5fd">{outc[:55]}</text>
  <text x="{conv_x+NR+16}" y="{conv_y+9}" font-size="8" fill="#c4b5fd">{outc[55:110]}</text>''')

    else:
        # CONFLICT: separate outcome per PR, then converge to "if both merged" node
        has_merge_info = bool(ga.get("if_merge_sequence") or ga.get("recommendation"))

        for i, (pr, y) in enumerate(zip(prs, ys)):
            col  = PR_COLORS[i % len(PR_COLORS)]
            risk = pr.get("analysis", {}).get("risk", "medium")
            rc   = RISK_COLOR.get(risk, "#888")
            summ = e(pr.get("analysis", {}).get("summary", pr["title"])[:40])
            outc = e(pr.get("analysis", {}).get("outcome_if_merged", "")[:50])

            # root → PR node
            svg.append(f'''
  <path d="M{RX+NR+5},{root_y} Q{(RX+BX)//2},{y} {BX-NR},{y}"
        fill="none" stroke="{col}" stroke-width="1.8" marker-end="url(#a{gi}{i})"/>
  <circle cx="{BX}" cy="{y}" r="{NR}" fill="#161b22" stroke="{col}" stroke-width="2.5"/>
  <text x="{BX}" y="{y-7}" text-anchor="middle" font-size="11" fill="{col}" font-weight="800">#{pr["number"]}</text>
  <text x="{BX}" y="{y+7}" text-anchor="middle" font-size="9" fill="#8b949e">{e(pr["author"])}</text>
  <rect x="{BX+NR+4}" y="{y-14}" width="160" height="28" rx="4" fill="#161b22" stroke="#30363d"/>
  <text x="{BX+NR+8}" y="{y}" font-size="8" fill="#e6edf3">{summ}</text>
  <text x="{BX+NR+8}" y="{y+12}" font-size="7.5" fill="{rc}">Risk: {risk}</text>''')

            # PR node → its own outcome node
            svg.append(f'''
  <line x1="{BX+NR+168}" y1="{y}" x2="{OX-NR-4}" y2="{y}"
        stroke="{col}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#a{gi}{i})"/>
  <circle cx="{OX}" cy="{y}" r="{NR-2}" fill="#1a1a2e" stroke="{col}" stroke-width="2"/>
  <text x="{OX}" y="{y-5}" text-anchor="middle" font-size="8" fill="{col}" font-weight="700">after</text>
  <text x="{OX}" y="{y+7}" text-anchor="middle" font-size="8" fill="{col}">#{pr["number"]}</text>
  <rect x="{OX+NR+4}" y="{y-16}" width="155" height="32" rx="4" fill="#1a1a2e" stroke="{col}" stroke-opacity="0.4"/>
  <text x="{OX+NR+7}" y="{y-3}" font-size="7.5" fill="#c9d1d9">{outc[:40]}</text>
  <text x="{OX+NR+7}" y="{y+10}" font-size="7.5" fill="#c9d1d9">{outc[40:80]}</text>''')

            # Each outcome → merge convergence node (if conflict has a meeting point)
            if has_merge_info:
                svg.append(f'''
  <path d="M{OX+NR+163},{y} Q{(OX+MX)//2+20},{(y+root_y)//2} {MX-NR-4},{root_y}"
        fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="4,4" opacity="0.6" marker-end="url(#am{gi})"/>''')

        # Merge convergence node — "if both merged"
        if has_merge_info:
            merge_text  = e(ga.get("if_merge_sequence", "")[:55])
            rec_text    = e(ga.get("recommendation", "")[:55])
            svg.append(f'''
  <circle cx="{MX}" cy="{root_y}" r="{NR+6}" fill="#1a0a2e" stroke="#8b5cf6" stroke-width="2.5" stroke-dasharray="6,3"/>
  <text x="{MX}" y="{root_y-8}" text-anchor="middle" font-size="9" fill="#8b5cf6" font-weight="700">if both</text>
  <text x="{MX}" y="{root_y+5}" text-anchor="middle" font-size="8" fill="#a78bfa">merged</text>
  <rect x="{MX+NR+8}" y="{root_y-28}" width="195" height="56" rx="6" fill="#1a0a2e" stroke="#8b5cf6" stroke-opacity="0.4"/>
  <text x="{MX+NR+12}" y="{root_y-14}" font-size="7.5" fill="#a78bfa" font-weight="600">Sequence:</text>
  <text x="{MX+NR+12}" y="{root_y}" font-size="7.5" fill="#c9d1d9">{merge_text[:55]}</text>
  <text x="{MX+NR+12}" y="{root_y+14}" font-size="7.5" fill="#c9d1d9">{rec_text[:55]}</text>''')

    svg.append("</svg>")
    return "\n".join(svg)

# ── Conflict HTML ─────────────────────────────────────────────────────────────

def build_conflict_html(groups):
    now      = datetime.now().strftime("%d %b %Y %H:%M")
    sections = []

    for gi, group in enumerate(groups):
        cat  = group["category"].replace("_"," ").title()
        prs  = group["prs"]
        ga   = group.get("analysis") or {}

        svg_html = _svg_tree(group, gi)

        pref       = str(ga.get("preferred_pr", "neither"))
        pref_label = f"Prefer PR #{pref}" if pref not in ("both","neither") else pref.capitalize()
        pref_color = "#22c55e" if pref not in ("neither",) else "#f59e0b"
        comp_cards = ""
        if True:  # single analysis card for the whole group
            comp_cards = f"""
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-top:14px">
                <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:12px;border-radius:0 8px 8px 0;margin-bottom:10px">
                    <div style="font-size:11px;font-weight:700;color:#92400e;text-transform:uppercase;margin-bottom:4px">Why They Conflict</div>
                    <div style="font-size:13px;color:#78350f">{e(ga.get('why_they_conflict',''))}</div>
                </div>
                <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:12px;border-radius:0 8px 8px 0;margin-bottom:10px">
                    <div style="font-size:11px;font-weight:700;color:#15803d;text-transform:uppercase;margin-bottom:4px">Shared Goal</div>
                    <div style="font-size:13px;color:#166534">{e(ga.get('shared_goal',''))}</div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
                    <div style="background:#eff6ff;border-radius:8px;padding:10px">
                        <div style="font-size:11px;font-weight:700;color:#1d4ed8;text-transform:uppercase;margin-bottom:4px">Recommended Merge Sequence</div>
                        <div style="font-size:12px;color:#1e3a5f">{e(ga.get('if_merge_sequence',''))}</div>
                    </div>
                    <div style="background:#111827;border-radius:8px;padding:10px">
                        <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:6px">&#129302; Recommendation</div>
                        <div style="font-size:12px;color:#e5e7eb;line-height:1.5;margin-bottom:8px">{e(ga.get('recommendation',''))}</div>
                        <span style="background:{pref_color};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700">{pref_label}</span>
                    </div>
                </div>
            </div>"""

        pr_details = "".join(
            f'<div style="flex:1;min-width:340px">{pr_detail_block(pr, PR_COLORS[i % len(PR_COLORS)])}</div>'
            for i, pr in enumerate(prs)
        )

        sections.append(f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;margin-bottom:32px;box-shadow:0 2px 8px rgba(0,0,0,.06)">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px">
                <span style="background:#dc2626;color:#fff;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:700">IDEA CONFLICT</span>
                <span style="background:#f3f4f6;color:#374151;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:600">Category: {cat}</span>
                <span style="font-size:13px;color:#6b7280">{len(prs)} PRs solving the same problem differently</span>
            </div>
            <div style="font-size:13px;color:#374151;padding:10px;background:#fffbeb;border-radius:6px;border-left:3px solid #f59e0b;margin-bottom:16px">
                <strong>Shared problem:</strong> {e(group.get('problem', ''))}
            </div>
            {svg_html}
            {comp_cards}
            <div style="margin-top:20px">
                <div style="font-size:13px;font-weight:700;margin-bottom:12px">Full PR Details</div>
                <div style="display:flex;gap:16px;flex-wrap:wrap">{pr_details}</div>
            </div>
        </div>""")

    body = "\n".join(sections) if sections else '<p style="color:#6b7280;padding:40px;text-align:center">No idea conflicts detected.</p>'
    return _html_page("PR Idea Conflicts", f"&#9889; PR Idea Conflict Analysis",
                      f"{REPO} &middot; {now} &middot; {len(groups)} conflict group(s)", body, bg="#f3f4f6")

# ── Isolated HTML ─────────────────────────────────────────────────────────────

def build_isolated_html(isolated):
    now   = datetime.now().strftime("%d %b %Y %H:%M")
    cards = "".join(
        f'<div style="margin-bottom:20px">{pr_detail_block(pr)}</div>'
        for pr in sorted(isolated, key=lambda x: x["created_at"])
    )
    body = cards or '<p style="color:#6b7280;padding:40px;text-align:center">No isolated PRs.</p>'
    return _html_page("Isolated PRs", "&#9989; Isolated PRs &mdash; Unique Problems",
                      f"{REPO} &middot; {now} &middot; {len(isolated)} PR(s)", body, bg="#f3f4f6")

def _html_page(title, h1, subtitle, body, bg="#f3f4f6"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title} &mdash; MiniChain</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:{bg};color:#111;padding:24px}}
  h1{{font-size:22px;font-weight:800;margin-bottom:4px}}
  .sub{{font-size:13px;color:#6b7280;margin-bottom:28px}}
  code{{font-family:monospace;background:#f3f4f6;padding:1px 5px;border-radius:3px}}
  a{{color:#1d4ed8}} h4{{color:#374151}}
</style>
</head>
<body>
<h1>{h1}</h1>
<p class="sub">{subtitle}</p>
{body}
</body>
</html>"""