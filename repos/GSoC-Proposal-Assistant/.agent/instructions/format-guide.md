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

---

## Section 2 — Abstract

- 1 paragraph, 100–200 words
- Must be specific and technical — NOT a rephrasing of the idea list description
- Must mention: the problem, your approach, key technologies, expected outcome

---

## Section 3 — Resume & Table of Contents

- Keep resume short (5-10 lines max).
- Include TOC if PDF is longer than 4 pages.

---

## Section 4 — Architecture Diagram (CRITICAL SECTION)

- Show final expected architecture of what you plan to deliver.
- Mid-level detail: components, connections, data flow, interfaces.
- Reference sequence diagrams and component diagrams.

---

## Section 5 — Detailed Architecture Description

Write 1–3 paragraphs per major component shown in the diagram:
- What does it do?
- Why this approach (vs alternatives)?
- How does it interact with other components?
- What are the implementation risks?

---

## Section 6 — Future Expansion (REQUIRED for AI-era proposals)

Demonstrates innovation capacity:
1. **Base Idea Completion** — estimate weeks
2. **Extension Y** — novel idea aligned with an AOSSIE theme
3. **Extension Z** — second novel idea

---

## Section 7 — PR Contributions List

Format:
```
Merged PRs:
- [PR Title] — https://github.com/AOSSIE-Org/RepoName/pull/123 (Mentor: @mentor_name)

Pending PRs:
- [PR Title] — https://github.com/AOSSIE-Org/RepoName/pull/456
```
