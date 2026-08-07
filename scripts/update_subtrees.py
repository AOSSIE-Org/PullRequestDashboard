import os
import re
import sys
import logging
import httpx
from pathlib import Path

# Add parent directory to sys.path to import repo_metadata
script_dir = Path(__file__).resolve().parent
bot_root = script_dir.parent
sys.path.insert(0, str(bot_root))

from repo_metadata import REPO_METADATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("subtree-sync")

# Key context files to sync from remote client repositories
KNOWN_CONTEXT_FILES = [
    ".agent/info/operational-data.md",
    ".agent/core/architecture.md",
    ".agent/core/code-mapping.md",
    ".agent/core/edge-cases.md",
    ".agent/core/examples.md",
    ".agent/instructions/setup.md",
    ".agent/instructions/testing.md",
    ".agent/instructions/deployment.md",
    ".agent/instructions/ci-cd.md",
    ".agent/instructions/format-guide.md",
    ".agent/instructions/checklist.md",
    ".agent/instructions/bad-patterns.md",
    "references/checklist.md",
    "references/format-guide.md",
    "references/bad-patterns.md",
    "SKILL.md",
    "AGENTS.md",
    "README.md",
]


def parse_github_url(url: str) -> tuple[str, str, str]:
    """Parse owner, repo, and ref from GitHub URL."""
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+))?", url)
    if match:
        owner, repo, ref = match.groups()
        repo = repo.removesuffix(".git")
        ref = ref or "main"
        return owner, repo, ref
    return "", "", "main"


def sync_repo_context(repo_name: str, meta: dict, client: httpx.Client):
    """Fetch specified .agent context files directly from raw GitHub endpoint."""
    url = meta.get("url")
    if not url:
        logger.warning(f"No URL defined for {repo_name}, skipping.")
        return

    owner, repo, ref = parse_github_url(url)
    if not owner or not repo:
        logger.error(f"Invalid GitHub URL for {repo_name}: {url}")
        return

    logger.info(f"Syncing context for '{repo_name}' ({owner}/{repo}@{ref})...")
    target_dir = bot_root / "repos" / repo_name
    target_dir.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "PullRequestDashboard-Context-Sync"}
    downloaded_count = 0

    for rel_file in KNOWN_CONTEXT_FILES:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{rel_file}"
        try:
            res = client.get(raw_url, headers=headers)
            if res.status_code == 200:
                dest_path = target_dir / rel_file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_bytes(res.content)
                logger.info(f"Downloaded: repos/{repo_name}/{rel_file}")
                downloaded_count += 1
        except Exception as e:
            logger.debug(f"Failed downloading {rel_file} for {repo_name}: {e}")

    logger.info(f"Synced {downloaded_count} context files into repos/{repo_name}")


def sync_all_subtrees():
    os.chdir(bot_root)
    repos_dir = bot_root / "repos"
    repos_dir.mkdir(exist_ok=True)

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for repo_name, meta in REPO_METADATA.items():
            sync_repo_context(repo_name, meta, client)


if __name__ == "__main__":
    sync_all_subtrees()
