import logging
from pathlib import Path

logger = logging.getLogger("pr-dashboard.context")


def get_repo_dir(repo_name: str) -> Path | None:
    """Find repository context directory inside repos/ or workspace."""
    bot_root = Path(__file__).resolve().parent
    candidates = [
        bot_root / "repos" / repo_name,
        bot_root / repo_name,
        bot_root.parent / repo_name,
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def load_full_repo_context(repo_name: str) -> str:
    """Dynamically scan and load ALL markdown files inside repos/<repo_name>/ without hardcoding file lists."""
    repo_dir = get_repo_dir(repo_name)
    if not repo_dir:
        logger.warning(f"Repository directory for '{repo_name}' not found.")
        return f"=== REPOSITORY: {repo_name} ==="

    context_parts = [f"=== REPOSITORY: {repo_name} ==="]
    loaded_files = 0

    # Recursively scan for all .md files inside the target repository directory
    for md_file in sorted(repo_dir.rglob("*.md")):
        # Skip internal cache or git folders
        if any(part.startswith(".") and part not in [".agent"] for part in md_file.parts):
            continue

        rel_path = md_file.relative_to(repo_dir)
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    context_parts.append(f"--- {rel_path} ---\n{content}")
                    loaded_files += 1
        except Exception as e:
            logger.error(f"Error reading context file {md_file}: {e}")

    logger.info(f"Loaded {loaded_files} markdown context files for '{repo_name}'")
    return "\n\n".join(context_parts)
