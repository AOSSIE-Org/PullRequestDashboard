<div align="center">
<h1>PR Dashboard</h1>
<h3>See which open pull requests overlap, and what order to merge them in</h3>
</div>

**PR Dashboard** is a command-line tool that helps maintainers work through a backlog of pull requests on any GitHub repository.

* **Why:** when several PRs solve the same problem or touch the same code, maintainers often find out only after merging one of them.
* **Who:** maintainers of any GitHub repository with more than a handful of open PRs.
* **What:** it fetches the PRs with the GitHub CLI, groups the ones that solve the same problem, and asks a local model to explain each group and suggest a merge order. It writes two HTML reports and opens them in your browser.
* **How:** `python main.py your-org/your-repo`. It needs `gh` and Ollama; nothing else.

Everything runs on your machine: no API fees, and no code is sent anywhere except the `gh` calls to GitHub.

**Example:** [AOSSIE's example output](https://aossie-org.github.io/PullRequestDashboard/) shows the two reports for a real repository.

---

## 🚀 Key Features

* **PR Grouping**: Embeds each PR's title and review summary with sentence-transformers (`all-MiniLM-L6-v2`) and groups the ones that solve the same problem. No model call is needed for grouping.
* **Conflict Graph**: `conflicts_tree.html` shows each group of overlapping PRs, with a local model's explanation of why they conflict, which PR to prefer, a suggested merge order, and each PR's risk.
* **Isolated PRs**: `isolated_prs.html` lists PRs that overlap with nothing else, so they can be reviewed and merged on their own.
* **Project-Aware**: The model is given a short summary of your project, taken from the repository's `AGENTS.md` or `README.md`, or from your own `context.md`.
* **Fully Local**: Grouping and analysis run on your machine through Ollama.

---

## 💻 Tech Stack

* **GitHub access**: GitHub CLI (`gh`)
* **Embeddings & Grouping**: sentence-transformers (`all-MiniLM-L6-v2`)
* **Local Model Server**: Ollama (default `llama3.2`)
* **Programming Language**: Python 3.10+
* **Reports**: static HTML

---

## 🏁 Getting Started

### 1. Get the code

Click **Use this template** at the top of this page to make your own copy, or clone this repository directly:

```bash
git clone https://github.com/AOSSIE-Org/PullRequestDashboard.git
cd PullRequestDashboard
```

### 2. Install

* **Python 3.10+**
* **[Ollama](https://ollama.com/download)**, then pull a model: `ollama pull llama3.2`
* **[GitHub CLI](https://cli.github.com/)**, logged in with `gh auth login`. The account needs read access to the repository you analyse.

```bash
python -m venv venv
source venv/bin/activate        # Windows (PowerShell): .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The first run downloads the embedding model (about 90 MB).

### 3. Run

```bash
python main.py your-org/your-repo
```

The two reports open in your browser when the run finishes:

* `conflicts_tree.html`: groups of PRs that solve the same problem, with a suggested merge order.
* `isolated_prs.html`: PRs that overlap with nothing else.

Each group and each isolated PR is one call to the local model, so a run over 20 PRs takes a few minutes on an ordinary computer.

### Optional settings

To avoid typing the repository every time, copy `.env.example` to `.env` and set `TARGET_REPO`. Other settings:

| Setting | Default | What it does |
|---|---|---|
| `PR_STATE` | `open` | Which PRs to analyse: `open`, `closed` or `all`. |
| `PR_LIMIT` | `20` | How many of the most recently updated PRs to analyse (up to 100). |
| `OLLAMA_MODEL` | `llama3.2:latest` | Local model used to explain groups and PRs. |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Where Ollama runs. |

Grouping sensitivity is set by `THRESHOLD` and `MIN_SIZE` at the top of [`grouping.py`](./grouping.py).

### Getting better results

* **Use an AI reviewer such as [CodeRabbit](https://coderabbit.ai).** PR Dashboard groups PRs by the summary it posts on each PR. Without one, it groups by PR title alone, which is much less accurate.
* **Give the model a short project summary.** It reads the first 1,000 characters of your repository's `AGENTS.md`, or `README.md` if there is no `AGENTS.md`. If those don't start with a clear description, put a short `context.md` (what the project is and how its code is organized) next to `main.py`; it is used instead.

---

## 🙌 Contributing

Contributions are welcome. See the [Contribution Guidelines](./CONTRIBUTING.md).

---

## 📍 License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
