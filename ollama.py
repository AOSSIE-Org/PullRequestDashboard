"""
ollama.py — Ollama interactions
Flow:
  1. group_prs_pass()    — one combined call: all PR walkthroughs + repo context → groupings
  2. analyse_group()     — deep call per conflict group (all PRs in group together)
  3. analyse_single_pr() — for isolated PRs
"""

import json, re, time
import urllib.request

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

# ── Core call ─────────────────────────────────────────────────────────────────

def _call(prompt, retries=2):
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 2000}
    }).encode("utf-8")

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                OLLAMA_URL, data=payload,
                headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = resp.read().decode("utf-8")
                if not body.strip():
                    print(f"    Empty response (attempt {attempt+1})")
                    continue
                raw = json.loads(body).get("response", "").strip()
                if not raw:
                    print(f"    Empty .response (attempt {attempt+1})")
                    continue
                raw = re.sub(r"```json|```", "", raw).strip()
                m = re.search(r"\{.*\}", raw, re.DOTALL)
                if m:
                    return json.loads(m.group(0))
                return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"    JSON parse error (attempt {attempt+1}): {e}")
        except Exception as e:
            print(f"    Ollama error (attempt {attempt+1}): {e}")
        time.sleep(2)
    return None

def check_ollama():
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=3)
        return True
    except Exception:
        return False

# ── Step 2: Combined first-pass — all PRs in one call ────────────────────────

def group_prs_pass(pr_data, repo_context=""):
    """
    Pass ALL PR walkthroughs + changes in one prompt.
    Returns Ollama's grouping of which PRs solve the same problem.
    """
    context_block = ""
    if repo_context:
        context_block = f"""== REPO CONTEXT ==
{repo_context}
== END CONTEXT ==

"""

    pr_blocks = ""
    for pr in pr_data:
        cr = pr.get("coderabbit") or {}
        wt = cr.get("walkthrough", "not available")
        ch = cr.get("changes", "")
        pr_blocks += f"""
--- PR #{pr['number']} by {pr['author']} ---
Title: {pr['title']}
Files: {', '.join(pr['files'][:15])}
Walkthrough:
{wt}
Changes:
{ch}
"""

    pr_num_list = [pr["number"] for pr in pr_data]
    prompt = f"""{context_block}You are reviewing pull requests for MiniChain — a minimal educational Python blockchain.

Below are {len(pr_data)} pull requests with their full CodeRabbit walkthroughs and changes.
{pr_blocks}

The ONLY valid PR numbers are: {pr_num_list}
Do NOT use any other PR numbers. Do NOT invent PR numbers.

Your task: group these PRs by the PROBLEM they solve, not by files.
Two PRs belong in the same group if they solve the same problem, even with different approaches.

Respond ONLY with a JSON object. No explanation. No markdown fences.
{{
  "groups": [
    {{
      "problem": "exact problem this group solves, 1 sentence",
      "problem_category": "one of: persistence, mempool, networking, validation, cli, testing, refactor, security, other",
      "pr_numbers": [list of PR numbers],
      "is_conflict": true or false
    }}
  ]
}}

STRICT RULES:
- Every PR number must appear in EXACTLY ONE group. Never repeat a PR number.
- A group with one PR is fine (isolated, is_conflict: false)
- is_conflict = true ONLY if 2 or more PRs are solving the same specific problem with different technical approaches
- Do NOT create multiple groups for the same PR
- Do NOT split a single PR across groups
- Total PR numbers across all groups must equal exactly {len(pr_data)}, no more no less.
"""
    valid_nums = set(pr["number"] for pr in pr_data)
    print("  Running combined grouping pass (all PRs together)...")
    result = _call(prompt)
    if not result or "groups" not in result:
        print("  Grouping failed — falling back to one group per PR")
        return [{"problem": pr["title"], "problem_category": "other",
                 "pr_numbers": [pr["number"]], "is_conflict": False}
                for pr in pr_data]

    # Strip hallucinated PR numbers
    cleaned = []
    hallucinated = []
    for g in result["groups"]:
        real = [n for n in g.get("pr_numbers", []) if n in valid_nums]
        fake = [n for n in g.get("pr_numbers", []) if n not in valid_nums]
        if fake:
            hallucinated.extend(fake)
        if real:
            cleaned.append({**g, "pr_numbers": real})

    if hallucinated:
        print(f"  WARNING: Ollama hallucinated PR numbers {hallucinated} — stripped")

    return cleaned

# ── Step 3: Deep analysis per conflict group ──────────────────────────────────

def analyse_group(group_meta, prs_in_group, repo_context=""):
    """Deep analysis of a conflict group — all PRs passed together."""
    context_block = f"Repo context:\n{repo_context[:1000]}\n\n" if repo_context else ""

    pr_blocks = ""
    for pr in prs_in_group:
        cr = pr.get("coderabbit") or {}
        wt = cr.get("walkthrough", "")[:600]
        ch = cr.get("changes", "")[:400]
        pr_blocks += f"""
PR #{pr['number']} by {pr['author']}:
Files: {', '.join(pr['files'][:10])}
Walkthrough: {wt}
Changes: {ch}
"""

    prompt = f"""{context_block}These PRs all solve the same problem: "{group_meta['problem']}"
But they use different approaches. Analyse them together.
{pr_blocks}

Respond ONLY with a JSON object. No explanation. No markdown fences.
{{
  "shared_problem": "precise problem all PRs are solving",
  "shared_goal": "what all approaches agree on",
  "pr_analyses": [
    {{
      "pr_number": <number>,
      "approach": "how this PR solves the problem, 2 sentences",
      "what_changed": "3 key changes separated by |",
      "strengths": "1 sentence",
      "weaknesses": "1 sentence",
      "outcome_if_merged": "1 sentence",
      "open_questions": "questions for reviewer separated by |",
      "risk": "low or medium or high",
      "summary": "one sentence TL;DR"
    }}
  ],
  "why_they_conflict": "why these approaches conflict, 2 sentences",
  "if_merge_sequence": "recommended merge order and why, 2 sentences",
  "recommendation": "which PR to prefer and why, 2 sentences",
  "preferred_pr": "PR number as string, or both, or neither"
}}"""

    result = _call(prompt)
    return result

# ── Isolated PR analysis ──────────────────────────────────────────────────────

def analyse_single_pr(pr, repo_context=""):
    context_block = f"Repo context:\n{repo_context[:800]}\n\n" if repo_context else ""
    cr = pr.get("coderabbit") or {}
    wt = cr.get("walkthrough", "")[:800]
    ch = cr.get("changes", "")[:400]

    prompt = f"""{context_block}Analyse this pull request for MiniChain (minimal Python blockchain).

PR #{pr['number']}: {pr['title']}
Author: {pr['author']}
Files: {', '.join(pr['files'][:15])}
Walkthrough: {wt}
Changes: {ch}

Respond ONLY with a JSON object. No explanation. No markdown fences.
{{
  "approach": "2 sentences",
  "what_changed": "3 key changes separated by |",
  "strengths": "1 sentence",
  "weaknesses": "1 sentence",
  "outcome_if_merged": "1 sentence",
  "open_questions": "separated by |",
  "risk": "low or medium or high",
  "summary": "one sentence TL;DR"
}}"""

    result = _call(prompt)
    if not result:
        return {
            "approach": "Could not analyse.", "what_changed": pr["title"],
            "strengths": "Unknown", "weaknesses": "Unknown",
            "outcome_if_merged": "Unknown", "open_questions": "",
            "risk": "medium", "summary": pr["title"]
        }
    return result