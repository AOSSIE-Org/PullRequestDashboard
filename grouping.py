"""
grouping.py — semantic clustering via sentence-transformers
No LLM for grouping. Embeddings + community_detection instead.
Ollama only called AFTER groups are found, to explain WHY they conflict.
"""

from sentence_transformers import SentenceTransformer, util
from ollama import analyse_group, analyse_single_pr

MODEL_NAME = "all-MiniLM-L6-v2"   # ~90MB, downloads once, runs on CPU
THRESHOLD  = 0.55                  # similarity threshold — tune if too many/few matches
MIN_SIZE   = 2                     # min PRs to form a conflict group

def resolve_groups(pr_data, repo_context=""):
    """
    1. Embed each PR walkthrough using sentence-transformers
    2. Cluster by semantic similarity (community_detection)
    3. Groups with 2+ PRs = conflict → deep Ollama analysis
    4. Singletons = isolated → single Ollama analysis
    """
    print("\n  Loading embedding model (first run downloads ~90MB)...")
    model = SentenceTransformer(MODEL_NAME)

    # Build text to embed: title + walkthrough for each PR
    texts = []
    for pr in pr_data:
        cr  = pr.get("coderabbit") or {}
        wt  = cr.get("walkthrough", "")[:600]
        ch  = cr.get("changes", "")[:300]
        texts.append(f"{pr['title']}\n{wt}\n{ch}")

    print(f"  Embedding {len(pr_data)} PRs...")
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    print(f"  Clustering (threshold={THRESHOLD})...")
    clusters = util.community_detection(
        embeddings,
        min_community_size=MIN_SIZE,
        threshold=THRESHOLD
    )

    # clusters = list of lists of indices into pr_data
    # PRs not in any cluster are isolated
    clustered_indices = set(idx for cluster in clusters for idx in cluster)
    isolated_indices  = [i for i in range(len(pr_data)) if i not in clustered_indices]

    print(f"\n  Found {len(clusters)} conflict group(s), {len(isolated_indices)} isolated PR(s)")

    # Show similarity scores for transparency
    similarity_matrix = util.cos_sim(embeddings, embeddings)
    for ci, cluster in enumerate(clusters):
        pr_nums = [pr_data[i]["number"] for i in cluster]
        scores  = []
        for x in range(len(cluster)):
            for y in range(x+1, len(cluster)):
                s = float(similarity_matrix[cluster[x]][cluster[y]])
                scores.append(f"#{pr_nums[x]}&#{pr_nums[y]}={s:.2f}")
        print(f"  Group {ci+1}: PRs {pr_nums} — similarity: {', '.join(scores)}")

    conflict_groups = []
    isolated_prs    = []

    # ── Conflict groups ───────────────────────────────────────────────────────
    for cluster in clusters:
        prs = [pr_data[i] for i in cluster]
        pr_nums = [p["number"] for p in prs]

        # Build a pseudo group_meta for analyse_group
        group_meta = {
            "problem": f"PRs {pr_nums} grouped by semantic similarity",
            "problem_category": "unknown",
        }

        print(f"\n  Conflict group: PRs {pr_nums}")
        print(f"  Running deep group analysis with Ollama...")
        group_analysis = analyse_group(group_meta, prs, repo_context)

        if group_analysis and "pr_analyses" in group_analysis:
            pr_by_num = {p["number"]: p for p in prs}
            for pa in group_analysis["pr_analyses"]:
                n = pa.get("pr_number")
                if n in pr_by_num:
                    pr_by_num[n]["analysis"] = pa

        # Use avg similarity to guess duplicate vs conflict (NLI will improve this later)
        avg_sim = float(similarity_matrix[cluster[0]][cluster[1]]) if len(cluster) > 1 else 0
        gtype = "duplicate" if avg_sim > 0.75 else "conflict"
        conflict_groups.append({
            "category":   group_analysis.get("problem_category", "unknown") if group_analysis else "unknown",
            "problem":    group_analysis.get("shared_problem", f"PRs {pr_nums}") if group_analysis else f"PRs {pr_nums}",
            "prs":        prs,
            "analysis":   group_analysis or {},
            "group_type": gtype,
        })

    # ── Isolated PRs ──────────────────────────────────────────────────────────
    for i in isolated_indices:
        pr = pr_data[i]
        print(f"\n  Isolated PR #{pr['number']} — analysing...")
        pr["analysis"] = analyse_single_pr(pr, repo_context)
        isolated_prs.append(pr)

    return conflict_groups, isolated_prs