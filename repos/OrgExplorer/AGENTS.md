# AOSSIE Contributor Agent Framework

> You are operating under the AOSSIE Contributor Skills Framework.

## 1. Mandatory Project Baseline Context

At the start of ANY session or task, load these 3 core files to establish project baseline rules:
- [.agent/core/architecture.md](.agent/core/architecture.md) — Zero-backend browser architecture & client API boundaries.
- [.agent/core/code-mapping.md](.agent/core/code-mapping.md) — Directory layout (`src/components/`, `src/pages/`, `src/services/`).
- [.agent/core/edge-cases.md](.agent/core/edge-cases.md) — Rate limit handling, IndexedDB caching, and D3 graph memory leaks.

## 2. Task Intent Router

Load additional files as needed based on the user's current request:

### Onboarding & Setup
- [.agent/instructions/setup.md](.agent/instructions/setup.md) — Local installation commands & issue assignment check.

### Writing & Modifying Code
- [.agent/core/examples.md](.agent/core/examples.md) — Approved React 18 / D3 / Tailwind code patterns vs anti-patterns.

### Testing & Verification
- [.agent/instructions/testing.md](.agent/instructions/testing.md) — Vite build verification, manual dashboard checks, and DevTools audits.
- [.agent/instructions/ci-cd.md](.agent/instructions/ci-cd.md) — Load when user explicitly asks to debug failing CI, provides a PR link/number, or pastes CI logs.

### Pull Requests & Community
- [.agent/info/operational-data.md](.agent/info/operational-data.md) — Maintainer contacts, Discord channels, and message templates.

---

- **Completion Criterion:** Confirm compliance with mandatory baseline rules and active task files before completing work.
