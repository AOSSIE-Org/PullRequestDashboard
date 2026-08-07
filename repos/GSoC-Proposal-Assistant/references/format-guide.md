# Proposal Format Guide

Detailed specs for each section of the AOSSIE GSoC Detailed Description PDF.

---

## Section 1 — Header Block

Must appear at the very top of the PDF.

```
Title:        <Project(s) Name>: <One sentence describing what you will do>
Project(s) Size: Large (22 weeks) [or Medium if justified]
Discord:      @your_discord_username
PoC Repo:     https://github.com/your-username/poc-repo
```

**Title rules:**
- Format: `ProjectName: Short action sentence`
- Example: `Agora Blockchain: Implementation of new voting algorithms and zero-knowledge proofs for greater privacy`
- Example: `rein: Replacing WebSocket and Nut.js with WebRTC and Koffi for cross-platform screen mirroring`
- If it's a new project(s) not on the ideas list: `BabyNest: A mobile app for pregnancy using XYZ framework and approach ABC`
- ❌ Never: "My Proposal", "GSoC 2026 Application", contributor's name in title

**Project(s) Size:**
- AOSSIE prefers Large (22 weeks) but contributor must justify it
- If choosing Medium (12 weeks), explicitly explain why and what fills the remaining time
- In the AI era, small ideas that could be done in weeks must be padded with genuine extensions

**PoC Repo:**
- Must exist or be committed to before final submission
- README should include: what was tested, how to run, video/GIF of it working (if applicable)
- For `rein` specifically: must show WebRTC + Koffi replacing WebSocket + Nut.js, tested on Linux/Windows/macOS VMs

---

## Section 2 — Abstract

- 1 paragraph, 100–200 words
- Must be specific and technical — NOT a rephrasing of the idea list description
- Must mention: the problem, your approach, key technologies, expected outcome
- Must NOT be: a generic intro copied from the project(s) README

**Bad abstract example:**
> "I want to work on the rein project(s) which is a screen mirroring tool. I will improve it and add new features during GSoC."

**Good abstract example:**
> "rein currently uses WebSocket for signaling and Nut.js for input injection, which limits cross-platform reliability and performance. This proposal replaces WebSocket with WebRTC for peer-to-peer screen streaming and Nut.js with Koffi for native input handling, tested across Linux, Windows, and macOS. Beyond this migration, I propose extending rein with adaptive bitrate streaming and a web-based receiver client, enabling use cases beyond the current Electron-only stack. These extensions align with AOSSIE's Communication theme and represent novel contributions beyond the existing ideas list."

---

## Section 3 — Resume

- Keep it short: 5–10 lines max
- Relevant items only: CS education, relevant project(s), open source contributions
- Do NOT include: high school achievements, unrelated internships, generic skills lists
- May be excluded if contributor prefers (form says "maybe")

---

## Section 4 — Table of Contents

Include if the PDF is longer than 4 pages. Link sections with page numbers if the tool supports it.

---

## Section 5 — Architecture Diagram (CRITICAL SECTION)

This is where most proposals fail. Requirements:

**What it must show:**
- The final expected architecture of what you plan to DELIVER — not the current state of the codebase
- Mid-level detail: components, connections, data flow, interfaces
- NOT a high-level 3-box diagram ("Frontend → Backend → DB")
- NOT a screenshot of the existing README diagram without modification

**How to create a good one:**
- Reference the existing README architecture diagram and show how yours EXTENDS or CHANGES it
- Reference sequence diagrams from CodeRabbit reviews under merged PRs for style guidance
- If the diagram is large, rotate it landscape or break into multiple sub-diagrams (component view, data flow view, etc.)
- Tools: draw.io, Mermaid, Excalidraw, Figma — export as image embedded in PDF

**Checklist for the diagram:**
- [ ] Shows new components the contributor will add (not just existing ones)
- [ ] Shows interfaces between components (protocols, APIs, events)
- [ ] Labels are specific (e.g., "WebRTC PeerConnection" not just "connection")
- [ ] Has a legend if using non-obvious notation
- [ ] Is readable at normal PDF zoom (not tiny)

---

## Section 6 — Detailed Architecture Description

Write 1–3 paragraphs per major component shown in the diagram. For each:
- What does it do?
- Why this approach (vs alternatives)?
- How does it interact with other components?
- What are the implementation risks?

---

## Section 7 — Challenges & Solutions (Optional but Recommended)

List technical challenges — not just GSoC-process challenges. Examples:
- Cross-platform native bindings (Koffi on Windows ARM)
- WebRTC NAT traversal in corporate networks
- Race conditions in concurrent PR indexing

For each challenge, reference which part of your proposed architecture addresses it.

---

## Section 8 — Packaging & Testing Plan

Must include:
- How the project(s) will be packaged (e.g., electron-forge, electroBun, npm package)
- Testing strategy: unit tests, integration tests, E2E tests
- Platforms tested: Linux, Windows, macOS (with VM evidence in PoC if applicable)
- CI/CD: any GitHub Actions or automated test pipelines planned

---

## Section 9 — Future Expansion (REQUIRED for AI-era proposals)

This section demonstrates innovation capacity — explicitly required by AOSSIE admins in 2026.

Structure:
1. **Base Idea Completion** — what from the ideas list you'll finish and when (estimate weeks)
2. **Extension Y** — novel idea aligned with an AOSSIE theme, with brief technical justification
3. **Extension Z** — second novel idea, or deeper elaboration of Y

AOSSIE Focus Themes (from ideas list):
- Don't own / Open source
- Decentralized Economic and Financial Stability
- User-Empowering Sunny Tools
- Trust
- Education
- Communication
- Governance and Management

Each extension must map to at least one theme.

---

## Section 10 — PR Contributions List

Format:
```
Merged PRs:
- [PR Title] — https://github.com/AOSSIE-Org/RepoName/pull/123 (Mentor: @mentor_name)
- ...

Pending PRs:
- [PR Title] — https://github.com/AOSSIE-Org/RepoName/pull/456
- ...
```

Rules:
- List ALL merged and pending PRs
- Include mentor name for each merged PR where applicable
- Do not just say "I have N merged PRs" without links
- Quality > quantity (AOSSIE explicitly states this)