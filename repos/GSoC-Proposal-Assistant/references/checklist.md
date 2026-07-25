# Proposal Review Checklist

Use this for REVIEWER mode. Evaluate each item and mark: ✅ Pass / ⚠️ Weak / ❌ Fail

---

## BLOCK 0 — Basics

- [ ] Proposal is written entirely in English
- [ ] Title follows format: `<Project(s) Name>: <Short action sentence>`
- [ ] Title does NOT contain contributor's own name
- [ ] Title is NOT generic ("GSoC Proposal", "My Proposal", etc.)
- [ ] Discord username is present
- [ ] PoC repo link is present and reachable
- [ ] Project(s) size is stated (Large/Medium) with justification

---

## BLOCK 1 — Abstract

- [ ] Abstract is specific and technical (not a copy of the idea list description)
- [ ] Mentions the specific problem being solved
- [ ] Mentions the specific approach / key technologies
- [ ] Does NOT start with "I want to work on..."
- [ ] Does NOT include phrases like "I am passionate about..." or "I believe..."

---

## BLOCK 2 — Architecture Diagram

- [ ] Diagram exists (not missing entirely)
- [ ] Shows the FINAL expected architecture, not just current state
- [ ] Mid-level detail: components, connections, interfaces labeled
- [ ] NOT a generic 3-box high-level diagram
- [ ] NOT a copy-paste of existing README diagram without modification
- [ ] New components the contributor will ADD are visible and labeled
- [ ] Readable at normal zoom

---

## BLOCK 3 — Detailed Architecture

- [ ] Each major component has a written description
- [ ] Explains WHY this approach (vs alternatives)
- [ ] Covers component interactions
- [ ] Identifies at least one implementation risk per major component

---

## BLOCK 4 — Timeline & Feasibility

- [ ] Covers full project(s) size (22 weeks for Large)
- [ ] Does NOT have generic week descriptions like "Week 1: Setup environment"
- [ ] Each week/phase has a specific, verifiable deliverable
- [ ] The base idea is NOT presented as taking the ENTIRE duration (leaves room for extensions)
- [ ] Extensions Y and Z are allocated real time, not just mentioned as "future work"

---

## BLOCK 5 — Future Expansion / Innovation

- [ ] At least one extension beyond the base idea is proposed
- [ ] Extensions are mapped to an AOSSIE theme
- [ ] Extensions are technically justified (not vague aspirations)
- [ ] Contributor shows they have thought about these independently (not AI-generated filler)

---

## BLOCK 6 — PR Contributions

- [ ] All merged PRs are listed with links
- [ ] All pending PRs are listed with links
- [ ] Mentor names are mentioned for merged PRs
- [ ] Does NOT just say "I have X merged PRs" without links
- [ ] Quality of PRs is evident from titles (not trivial fixes unless genuinely impactful)

---

## BLOCK 7 — PoC

- [ ] PoC repo exists
- [ ] PoC README explains what was tested
- [ ] PoC demonstrates the core technical risk of the proposal
- [ ] For rein: tests WebRTC + Koffi on Linux, Windows, macOS VMs
- [ ] Video or GIF evidence present (recommended)

---

## BLOCK 8 — Red Flags (Instant ⚠️ or ❌)

Check for these patterns that indicate AI-dumping or low-effort proposals:

- [ ] (No flag) Abstract reads like it was written by an LLM with no personalization
- [ ] (No flag) Architecture section is generic and could apply to ANY project(s)
- [ ] (No flag) Challenges section lists process challenges ("time management", "learning curve") instead of technical challenges
- [ ] (No flag) Timeline is perfectly even across all weeks (real project(s) are uneven)
- [ ] (No flag) "Future work" section is vague ("improve performance", "add more features")
- [ ] (No flag) No mention of specific files, functions, or existing code in the codebase
- [ ] (No flag) Proposal doesn't reference any AOSSIE-specific tools (CodeRabbit, specific repo patterns)

---

## Final Verdict

**Ready to Submit:** All blocks pass, no ❌, max 2 ⚠️
**Needs Work:** 1–3 ❌ or 5+ ⚠️ — specify what to fix
**Major Rework Required:** 4+ ❌ or architecture diagram missing entirely