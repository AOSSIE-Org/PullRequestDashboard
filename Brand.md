# Brand Guidelines

This document outlines the brand guidelines, visual identity, and communication tone for the **AOSSIE Skills Ecosystem**, of which **Pull Request Dashboard** is a core module.


## Visual Identity

### Logos and Assets

All official logos are stored in the [`/public`](./public) directory of this repository.

- **Skills Ecosystem Logo:** [`/public/skills-logo.svg`](./public/skills-logo.svg) — The primary logo for the project. A dark folder glyph with blurred red and blue "context" blobs and an orange highlight card, capped with pixel-art `SKILLS.MD` text. Represents the ecosystem's core idea: project knowledge (skills) captured and organized as living documentation.
- **AOSSIE Logo:** [`/public/aossie-logo.svg`](./public/aossie-logo.svg) — Parent organization mark. Used alongside the Skills Ecosystem logo in README headers and cross-org materials, never as a substitute for it.
- **Stability Nexus Badge:** [`/public/stability.svg`](./public/stability.svg) — Project stability status indicator, shown in README headers.

Use `skills-logo.svg` on dark or neutral backgrounds — its base fill (`#1C1818`) is designed to sit on dark surfaces; on light backgrounds, keep it inside a dark card/container rather than placing it directly on white.

### Color Palette

The palette is drawn directly from the Skills Ecosystem logo. It favors a dark, glass-like base with warm and cool accent blobs.

* **Folder Base (Dark Glass):** `#1C1818`
  * The logo's base fill. Use for dark surfaces, containers behind the logo, and code/DAG panels.
* **Signal Red (Primary Accent):** `#A82020`
  * The dominant logo blob color. Used for primary emphasis, warnings, and high-risk indicators (e.g. "High Risk" badges, conflict markers).
* **Signal Blue (Secondary Accent):** `#0C66A6`
  * The cooler logo blob color. Used for links, informational badges, and neutral data highlights.
* **Skills Orange (Highlight):** `#E37A4B`
  * Used for the logo's folder outline, the accent card, and the `SKILLS.MD` pixel text. This is the "call to action" color — use it for the most important highlight on a page (primary buttons, active states, key stat).
* **Report Surfaces (Generated HTML Reports):**
  * `#0d1117` — DAG/graph canvas background (matches GitHub's dark theme, since reports are read alongside GitHub).
  * `#161b22` — Node and card fill on dark canvases.
  * `#30363d` — Borders/dividers on dark canvases.
  * `#e6edf3` — Primary text on dark canvases.
  * `#8b949e` — Secondary/muted text on dark canvases.
* **Report Surfaces (Light Dashboard Pages):**
  * `#f3f4f6` — Page background.
  * `#ffffff` — Card background.
  * `#111827` / `#374151` — Primary / secondary text.
  * `#6b7280` — Muted text and metadata.
  * `#1d4ed8` — Links and primary buttons.
* **Risk Indicators:**
  * Low: `#22c55e` · Medium: `#f59e0b` · High: `#ef4444`
* **Accessibility Target:** All text pairings must meet or exceed WCAG 2.1 AA (4.5:1) contrast. On dark report canvases, use `#e6edf3` or lighter for body text — do not place `#8b949e` on `#1C1818` for anything beyond secondary labels.

## Typography

Generated reports and dashboard pages use system sans-serif fonts for fast rendering with zero external font loading (reports must open standalone, offline).

- **Primary Stack:** `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Monospace (file paths, code refs):** default system monospace (`font-family: monospace`)
- **Weights:**
  - Regular (400): Body copy, descriptions.
  - Semibold/Bold (600–800): Headings, badges, PR titles, stat values.
- **Sizes:**
  - `11px`–`12px`: Metadata, uppercase eyebrow labels, badges.
  - `13px`–`14px`: Body copy, table/list data.
  - `15px`–`18px`: Card and section headings.
  - `24px`+: Page titles.
- **Usage:** Uppercase, letter-spaced labels (e.g. "Idea Conflicts", "Maintainer Snapshot") mark category badges. Headings are bold; numerical/risk values should stand out with color + weight, not size alone.

## Terminology & Copywriting

When writing documentation, UI copy, or community announcements, strictly adhere to the following:

- **AOSSIE Skills Ecosystem** — the overall project (not "skills ecosystem" or "Skills ecosystem" mid-sentence unless it's clearly a continuation).
- **Pull Request Dashboard** / **PR Dashboard** — the module documented in this repository. Do not shorten further (e.g. not "PRD", which collides with "product requirements doc").
- **Skill Bot** (two words, capitalized) — the Discord assistant module.
- **Skill Updater** (two words, capitalized) — the knowledge-evolution/PR pipeline module.
- **Conflict DAG** — the interactive dependency graph rendered in `conflicts_tree.html`. Always capitalize DAG.
- **`context.md`**, **`gap_log.json`**, **`conflicts_tree.html`**, **`isolated_prs.html`** — always in inline code formatting when referenced, matching their exact on-disk filenames.
- **Local-first** (hyphenated, lowercase) — describes the tool's core design principle; use consistently rather than "local first" or "Local First".
