# Version Release Instructions (Maintainers Only)

> **Access Note:** Version releasing, tag creation, and deployment triggers are strictly restricted to repository maintainers with admin access.

## Delivery & Deployment Workflows

| Environment | Delivery Mechanism | Trigger |
| :--- | :--- | :--- |
| GitHub Pages | `.github/workflows/deploy.yml` | Pushes to `main` branch |
| Release Workflow | `.github/workflows/version-release.yml` | Pushing `VERSION` file updates to `main` |

## Maintainer Release Checklist

1. **Pre-Release Quality Verification**:
   ```bash
   npm run build
   npm run preview
   ```
2. **Version Bumping**:
   - Update `"version"` in `package.json` (e.g. `"1.0.1"`).
   - Update version string in `VERSION` file (e.g. `1.0.1`).
3. **Trigger Automated Release**:
   - Push commit updating `VERSION` to `main`.
   - The automated GitHub Action creates the release tag and publishes the GitHub release.
