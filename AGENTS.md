# AGENTS.md — PR Dashboard

PR Dashboard is a local maintainer tool for any GitHub repository: it fetches the repository's
PRs via the GitHub CLI, groups the ones that solve the same problem, asks a local Ollama model to
explain each group and suggest a merge order, and renders two static HTML reports — a conflict
graph and a list of isolated PRs. It is a standalone tool with no dependency on other projects.

## Setup & Run

```bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
gh auth login                   # GitHub CLI must be authenticated
ollama pull llama3.2            # or whatever OLLAMA_MODEL is set to
python main.py owner/repo       # or set TARGET_REPO in .env
```

Configuration lives in `config.py`, read from the command line, then `.env`, then defaults
(see `.env.example`): `TARGET_REPO`, `PR_STATE` (default `open`), `PR_LIMIT` (default 20),
`OLLAMA_MODEL`, `OLLAMA_URL`. Clustering sensitivity is `THRESHOLD` / `MIN_SIZE` at the top of
`grouping.py`. Never hard-code a repository or project name in code or prompts — use
`config.REPO` / `config.repo_name()`.

## Code Map

- `main.py` — entry point; orchestrates the pipeline described in its module docstring
  (load context → fetch PRs → cluster → analyse groups → analyse isolated PRs → render → open).
- `config.py` — run settings (see above) and a minimal `.env` reader.
- `github.py` — `gh` CLI wrapper: fetches PRs, changed files, CodeRabbit/Devin review summaries,
  and the project context (`fetch_repo_context`: local `context.md`, else the target repo's
  `AGENTS.md`, else its `README.md`). Prompts only use the first ~1,000 characters of it.
- `grouping.py` — embeds PR titles/review summaries with `sentence-transformers`
  (`all-MiniLM-L6-v2`) and clusters them into conflict groups.
- `ollama.py` — local model calls for per-group and per-isolated-PR analysis, with lenient JSON
  parsing for small-model output.
- `render.py` — builds `conflicts_tree.html` and `isolated_prs.html`. **These two HTML files are
  generated output** — don't hand-edit them, edit `render.py` and re-run `python main.py`.
- `generate_gh_pages_simulation.py` + `public/` — AOSSIE's example output, published to GitHub
  Pages by `deploy-gh-pages.yml` (AOSSIE-Org only). Not part of the analysis pipeline.

There is currently no automated test suite — verify changes by running `python main.py` end-to-end
against a real repository and inspecting the rendered HTML.

## Key Design Principles (from README — keep changes aligned with these)

1. **Context-grounded**: every PR evaluation must weigh the project context, not just the raw
   diff — while keeping that context short enough for a small local model.
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
  description (tool + scope). AOSSIE's AI policy also forbids unguided automatic
  issue/bug generation from a codebase scan.
- **Code style**: PEP 8, `black` formatting (enforced via pre-commit), type hints on new
  functions, docstrings on public functions/classes. Remove debug `print`s before committing.
