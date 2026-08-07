# CI/CD Workflows & Log Diagnosis

This instruction file guides AI agents on how to inspect, diagnose, and resolve failures across GitHub Actions workflows defined in `.github/workflows/`.

## Workflow Directory Map

| Workflow File | Purpose | Triggers | Primary Troubleshooting Command |
| :--- | :--- | :--- | :--- |
| `deploy.yml` | Builds and deploys site to GitHub Pages | Pushes to `main` | `npm run build` |
| `version-release.yml` | Automated version tagging & release | Push `VERSION` changes to `main` | Verify `VERSION` semver format |
| `label-merge-conflicts.yml` | Labels PRs with merge conflicts | Pull Request updates | Rebase branch against `main` |
| `sync-pr-labels.yml` | Manages PR & Issue label states | PR/Issue events | Check GitHub workflow permissions |

---

## Log Inspection Protocol

When requested to debug a failing CI workflow (via PR link, PR number, or pasted logs):

### 1. Log Retrieval with `gh` CLI

```bash
# Check PR checks & find failing run ID
gh pr checks <pr-number-or-link>

# Fetch logs for failing run
gh run view <run-id> --log-failed
```

### 2. Pre-Push Local Verification

```bash
npm run build
```
