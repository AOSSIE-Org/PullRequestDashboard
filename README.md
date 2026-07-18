<!-- Don't delete it -->
<div name="readme-top"></div>

<!-- Organization Logo -->
<div align="center" style="display: flex; align-items: center; justify-content: center; gap: 16px;">
  <img alt="AOSSIE" src="public/aossie-logo.svg" width="175">
  <img src="public/stability.svg" width="175" alt="Project stability status" />
</div>

&nbsp;

<!-- Organization Name -->
<div align="center">

[![Static Badge](https://img.shields.io/badge/aossie.org/PullRequestDashboard-228B22?style=for-the-badge&labelColor=FFC517)](https://github.com/AOSSIE-Org/PullRequestDashboard)
<!-- Correct deployed url to be added -->

</div>

<!-- Organization/Project Social Handles -->
<p align="center">
<!-- Telegram -->
<a href="https://t.me/StabilityNexus">
<img src="https://img.shields.io/badge/Telegram-black?style=flat&logo=telegram&logoColor=white&logoSize=auto&color=24A1DE" alt="Telegram Badge"/></a>
&nbsp;&nbsp;
<!-- X (formerly Twitter) -->
<a href="https://x.com/aossie_org">
<img src="https://img.shields.io/twitter/follow/aossie_org" alt="X (formerly Twitter) Badge"/></a>
&nbsp;&nbsp;
<!-- Discord -->
<a href="https://discord.gg/hjUhu33uAn">
<img src="https://img.shields.io/discord/1022871757289422898?style=flat&logo=discord&logoColor=white&logoSize=auto&label=Discord&labelColor=5865F2&color=57F287" alt="Discord Badge"/></a>
&nbsp;&nbsp;
<!-- LinkedIn -->
<a href="https://www.linkedin.com/company/aossie/">
  <img src="https://img.shields.io/badge/LinkedIn-black?style=flat&logo=LinkedIn&logoColor=white&logoSize=auto&color=0A66C2" alt="LinkedIn Badge"></a>
&nbsp;&nbsp;
<!-- Youtube -->
<a href="https://www.youtube.com/@AOSSIE-Org">
  <img src="https://img.shields.io/youtube/channel/subscribers/UCKVVLbawY7Gej_3o2WKsoiA?style=flat&logo=youtube&logoColor=white%20&logoSize=auto&labelColor=FF0000&color=FF0000" alt="Youtube Badge"></a>


[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/AOSSIE-Org/PullRequestDashboard/badge)](https://scorecard.dev/viewer/?uri=github.com/AOSSIE-Org/PullRequestDashboard)

[![Best Practices](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2FAOSSIE-Org%2FPullRequestDashboard%2Fmain%2Fchecklist-status.json&logo=openssf)](./BestPracticesChecklist.md)
</p>

---

<div align="center">
<h1>AOSSIE Pull Request Dashboard</h1>
<h3>Local-First Merge Analysis & Conflict Resolution Dashboard</h3>
</div>

**Pull Request Dashboard** (PR Dashboard) is a core module in the [AOSSIE Skills Ecosystem](https://github.com/AOSSIE-Org/skills). It is a local-first analysis tool designed to help project maintainers review incoming pull requests, identify semantic conflicts, analyze architectural gaps, and determine optimal merge sequences.

By querying the GitHub API via the GitHub CLI (`gh`), fetching PR diffs and automated AI Bot Reviewer (e.g., CodeRabbit, Devin) walkthrough summaries, loading codebase context (`context.md`), and calling local Ollama models, the tool generates a visual Conflict Directed Acyclic Graph (DAG) detailing merge reasoning and post-merge impacts.

---

## 🏗️ Role in the Skills Ecosystem

The PR Dashboard acts as the primary code quality and merge analysis layer for maintainers:

```mermaid
flowchart TD
    %% Nodes
    SC["<b><font color='#F59E0B'>Skills Context</font></b><br><br>Skills Core (Shared Org wide skills)<br>per-repo skills (AGENTS.md + skills/ directory)"]
    Contributors["Contributors"]
    Maintainers["Maintainers"]
    
    SB["<b><font color='#F59E0B'>Skill Bot</font></b> (Discord Assistant)<br><br>Answers contributor questions<br>using asked question-oriented project skills ➔ LLM fallback"]
    PD["<b><font color='#F59E0B'>PR Dashboard</font></b> (Merge Analysis)<br><br>Clusters PRs semantically, injects skills & communication(e.g. Discord) context.<br>Extracts PR changes briefly & open questions for maintainers to review.<br>Prepares Conflict DAG with merge reasoning & post-merge impact."]
    SU["<b><font color='#F59E0B'>Skill Updater</font></b> (Knowledge Evolution)<br><br>Collects all logs from different components.<br>Updates relevant repo-skills by asking maintainers or admins<br>to review and approve generated updates."]

    %% Edges
    %% Contributor Flow
    Contributors -- "Ask Questions in Discord" --> SB
    SC -- "Powers answers" --> SB
    SB -- "If gaps found, send logs for maintainers<br>to answer and update project skill via updater." --> SU

    %% Maintainer Flow
    Maintainers -- "Reviews PRs<br>with" --> PD
    SC -- "Powers reasoning" --> PD
    PD -- "If gaps found, send logs for maintainers<br>to answer and update those project skills via updater." --> SU

    %% Feedback Loop & Sync
    Maintainers -- "Collects communication platform (e.g. Discord) discussions, filters important<br>topics by giving that repo-skills context, and sends suggested updates to maintainers<br>to reformat or modify as needed (maintainer approve)" --> SU
    SU -- "PR Skill Updater bot opens PR for gap skills and<br>recently merged PR context (maintainers approve)" --> SC

    %% Style Classes
    classDef yellowBox fill:#1E293B,stroke:#F59E0B,stroke-width:2px,color:#F8FAFC;
    classDef purpleBox fill:#1E293B,stroke:#8B5CF6,stroke-width:2px,color:#F8FAFC;
    
    class SC,SB,PD,SU yellowBox;
    class Contributors,Maintainers purpleBox;
```


1. **Pull Request Fetching**: The dashboard connects to GitHub via `gh` to retrieve open/closed PRs, modified files, and AI Bot Reviewer (e.g., CodeRabbit, Devin) summaries.
2. **Context-Grounded Reasoning**: It reads the local repository context (`context.md`) and the global/per-repo skills from the Skills Core to evaluate PRs against the project rules.
3. **DAG Generation**: It renders an interactive Conflict DAG illustrating PR dependency relationships, suggested merge sequences, and post-merge impact.
4. **Gap Logging**: If the dashboard identifies any architectural gaps or changes not covered in the current skills context, it logs them to `gap_log.json` to be consumed by the [Skill Updater](https://github.com/kpj2006/skill-updater).

---

## 🚀 Key Features

* **Semantic PR Clustering**: Uses a local Ollama model to group and cluster PRs based on semantic similarity of code changes and modified subcomponents.
* **Conflict DAG Visualization**: Renders an interactive HTML report (`conflicts_tree.html`) detailing overlapping file conflicts, recommended merge sequences, and post-merge architectural impacts.
* **Isolated PR Filtering**: Identifies non-conflicting, independent PRs and lists them in `isolated_prs.html` for immediate, safe merging.
* **Local-First Analysis**: Executes all clustering, evaluation, and DAG reasoning locally through Ollama, ensuring data privacy with zero external API costs.
* **Feedback Loop Gap Signaling**: Emits gap events for the Skill Updater pipeline when developer PRs introduce architectural changes that are not documented in the skills.

---

## 💻 Tech Stack

* **CLI Integration**: GitHub CLI (`gh`)
* **Local Model Server**: Ollama (`qwen2.5:7b` / `llama3`)
* **Programming Language**: Python 3.10+
* **Report Rendering**: HTML5, Vanilla CSS, Tailwind CSS

---
## 🔗 Repository Links

1. [Skills Core Repository](https://github.com/AOSSIE-Org/Skills)
2. [Interactive Simulation](https://github.com/kpj2006/InteractiveSimulation) (Live Demo: [demo](https://kpj2006.github.io/InteractiveSimulation/))
3. [Skill Bot Assistant](https://github.com/AOSSIE-Org/SkillBot)
4. [Skill Updater Pipeline](https://github.com/kpj2006/skill-updater)


## 🏁 Getting Started

### Prerequisites

* **Python 3.10+**
* **Ollama** installed and running on your local machine.
* **GitHub CLI (`gh`)** installed and authenticated with your GitHub account:
  ```bash
  gh auth login
  ```

---

### Installation & Run

#### 1. Clone the Repository

```bash
git clone https://github.com/AOSSIE-Org/PullRequestDashboard.git
cd PullRequestDashboard
```

#### 2. Set Up Virtual Environment & Dependencies

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Setup Context File

Ensure you have a `context.md` file detailing the repository architecture inside the dashboard folder (a default context file for [MiniChain](https://github.com/StabilityNexus/MiniChain) is provided as `context.md`).

#### 4. Configuration

All configuration settings are defined at the top of each script file—no `.env` file is required.

* **`github.py`** — Set the target repository:
  
  ```python
  REPO = "StabilityNexus/MiniChain"  # ← Change to your repository
  ```

* **`grouping.py`** — Tune the clustering sensitivity:
  
  ```python
  THRESHOLD = 0.55   # Lower value = more groups, higher value = fewer but tighter groups
  MIN_SIZE  = 2      # Minimum PRs needed to form a conflict group
  ```

* **`ollama.py`** — Choose the local LLM model:
  
  ```python
  OLLAMA_MODEL = "qwen2.5:7b"  # Specify the Ollama model to use
  ```

* **Switch to Production Mode (Open PRs)** in **`github.py`**:
  
  By default, the dashboard runs on recent closed PRs for testing. Switch to open PRs for production:
  
  ```python
  # Comment out the test line, and uncomment the production line:
  # prs = gh(f"repos/{REPO}/pulls?state=closed&per_page=10&sort=updated&direction=desc")
  return gh_paginate(f"repos/{REPO}/pulls?state=open&per_page=100")
  ```

#### 5. Run the Dashboard

Execute the entry point script:

```bash
python main.py
```

The script will fetch the PRs, cluster them, generate the reports, and automatically open them in your default web browser:
* `conflicts_tree.html` (Conflict DAG & merge sequencing)
* `isolated_prs.html` (Independent, ready-to-merge PRs)

---

## 🗺️ Roadmap & Future Enhancements

The long-term development of Pull Request Dashboard is divided into several milestones outlined in the [roadmap.md](./roadmap.md).

---

## 🛡️ Key Design Principles

1. **Context-Grounded**: Always evaluate PRs against the project description, architectural rules, and Skills Core.
2. **Merge Safety First**: Prioritize highlighting overlapping modifications and architectural conflict risks.
3. **Local-First**: Keep codebase analysis, clustering, and reasoning offline using local Ollama models.
4. **Actionable Recommendations**: Every conflict group must present a suggested merge order with clear reasoning.

---

## 🙌 Contributing

⭐ Don't forget to star this repository if you find it useful! ⭐

Thank you for considering contributing to this project! Contributions are highly appreciated and welcomed. To ensure smooth collaboration, please refer to our [Contribution Guidelines](./CONTRIBUTING.md).

---

## ✨ Maintainers

* [Karun Pacholi](https://github.com/kpj2006) - Lead Developer & Architect
* [zahnentferner](https://github.com/Zahnentferner) - admin & reviewer


---

## 📍 License

This project is licensed under the GNU General Public License v3.0.
See the [LICENSE](LICENSE) file for details.

---

## 💪 Thanks To All Contributors

Thanks a lot for spending your time helping TODO grow. Keep rocking 🥂

[![Contributors](https://contrib.rocks/image?repo=AOSSIE-Org/PullRequestDashboard)](https://github.com/AOSSIE-Org/PullRequestDashboard/graphs/contributors)

© 2026 AOSSIE
