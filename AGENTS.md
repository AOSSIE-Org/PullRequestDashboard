# AGENTS.md — AOSSIE Pull Request Dashboard

PR Dashboard is a local-first maintainer tool: it fetches a target repository's PRs via the
GitHub CLI, clusters them semantically, evaluates each cluster against that repo's synced
context and local Ollama models, and renders two static HTML reports — a Conflict DAG with
suggested merge order, and a list of independent PRs safe to merge immediately. It is one module
of the [AOSSIE Skills Ecosystem](https://github.com/AOSSIE-Org/Skills); see that repo's
`AGENTS.md` for the ecosystem-wide picture.

## Setup & Run

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
gh auth login                   # GitHub CLI must be authenticated
ollama pull qwen2.5:7b          # or whatever OLLAMA_MODEL is set in ollama.py
python scripts/update_subtrees.py   # pulls context files for repos listed in repo_metadata.py
python main.py
```

There is no `.env` file — **all configuration lives as constants at the top of the relevant
script**, not environment variables:

- `github.py` — `REPO = "org/name"` (the target repo whose PRs get analyzed). Defaults to closed
  PRs for local testing; the open-PR fetch for production use is present but commented out in
  the same function — read the comment before switching it.
- `grouping.py` — `THRESHOLD` (clustering sensitivity) and `MIN_SIZE` (minimum PRs per conflict
  group).
- `ollama.py` — `OLLAMA_MODEL`.
- `repo_metadata.py` — `REPO_METADATA` dict mapping a repo's folder name to its GitHub URL, used
  by `scripts/update_subtrees.py` to know what to sync. **This must have an entry whose key
  matches `REPO`'s last path segment in `github.py`** (e.g. `REPO = "org/MiniChain"` needs a
  `"MiniChain"` key here) — otherwise `context.py` finds no folder under `repos/` and the
  analysis runs with zero repo context.

## Code Map

- `main.py` — current entry point; orchestrates the pipeline described in its own module
  docstring (load repo context via `context.py` → fetch PRs → cluster → analyze groups →
  analyze isolated PRs → render → open in browser).
- `github.py` — `gh` CLI wrapper: fetches PRs, diffs, and CodeRabbit/Devin bot review summaries.
- `context.py` — `load_full_repo_context(repo_name)` recursively reads every `.md` file under
  `repos/<repo_name>/` (skipping dotfiles/folders except `.agent`) and concatenates them into the
  context string passed to Ollama. Replaces the old single static `context.md` file.
- `repos/<repo_name>/` — per-repo context mirror, populated by `scripts/update_subtrees.py`
  (fetches `AGENTS.md`, `README.md`, `SKILL.md`, and the `.agent/**` files listed in
  `KNOWN_CONTEXT_FILES` directly from `raw.githubusercontent.com`, not an actual git subtree
  despite the script name). **Don't hand-edit files in here** — re-run the sync script instead,
  or add/fix the source file in the upstream repo.
- `repo_metadata.py` — see Setup above.
- `grouping.py` — embeds PR titles/bodies with `sentence-transformers` (`all-MiniLM-L6-v2`) and
  clusters them into conflict groups.
- `ollama.py` — local model calls for per-group and per-isolated-PR analysis.
- `render.py` — builds `conflicts_tree.html` and `isolated_prs.html`. **These two HTML files are
  generated output** — don't hand-edit them, edit `render.py` and re-run `python main.py`.
- `dashboard.py` — an earlier, self-contained monolithic version of the same pipeline (all
  `gh`/Ollama/grouping/rendering logic inlined in one file, hardcoded `OLLAMA_MODEL =
  "llama3.1:8b"`). It still runs standalone (`python dashboard.py`) but is **not** the maintained
  pipeline — treat `main.py` + `github.py`/`context.py`/`grouping.py`/`ollama.py`/`render.py` as
  the source of truth, and don't add new features to `dashboard.py`.
- `generate_gh_pages_simulation.py` — copies the root `conflicts_tree.html`/`isolated_prs.html`
  into `public/` with a "maintainer snapshot" banner, for the GitHub Pages demo deploy. Not part
  of the analysis pipeline itself.

There is currently no automated test suite (`scripts/` only holds `update_subtrees.py`) — verify
changes by running `python main.py` end-to-end against a real or fixture repo and inspecting the
rendered HTML.

> **README.md is stale**: it still documents a single static `context.md` file and doesn't
> mention `context.py`, `repos/`, `repo_metadata.py`, or `scripts/update_subtrees.py`. Trust this
> file and the code over the README's "Setup Context File" section until the README is updated.

## Key Design Principles (from README — keep changes aligned with these)

1. **Context-grounded**: every PR evaluation must weigh the synced repo context (`repos/`) and
   the Skills Core / per-repo skills, not just the raw diff.
2. **Merge safety first**: prioritize surfacing overlapping-file and architectural conflict
   risk over minimizing false positives.
3. **Local-first**: clustering, evaluation, and DAG reasoning stay offline via local Ollama
   models — don't introduce calls to hosted LLM APIs.
4. **Actionable recommendations**: every conflict group's output must include a suggested merge
   order with reasoning, not just a list of overlapping PRs.

## Contributing

- **Discord-first, mandatory**: all project communication happens on the
  [Discord server](https://discord.gg/hjUhu33uAn); post PR/issue updates there, not just on
  GitHub. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full workflow, branch/commit
  conventions, and pre-commit setup.
- **AI disclosure required**: if you used an AI tool for code, tests, or docs, say so in the PR
  description (tool + scope). This ecosystem's AI policy also forbids unguided automatic
  issue/bug generation from a codebase scan.
- **Code style**: PEP 8, `black` formatting (enforced via pre-commit), type hints on new
  functions, docstrings on public functions/classes. Remove debug `print`s before committing.
