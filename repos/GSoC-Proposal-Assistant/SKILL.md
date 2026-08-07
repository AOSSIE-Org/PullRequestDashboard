---
name: aossie-proposal-writer
description: >
  Use this skill whenever a contributor is writing, drafting, improving, or reviewing a GSoC proposal
  for AOSSIE (Australian Open Source Software Innovation and Education). Triggers on any mention of
  "GSoC proposal", "AOSSIE application", "proposal PDF", "detailed description", "proposal review",
  "am I ready to submit", "check my proposal", "help me write my proposal", or when a contributor
  pastes a draft and asks for feedback. This skill operates in two modes: HELPER (drafting from
  scratch) and REVIEWER (checking an existing draft). Always use this skill — do NOT try to wing
  GSoC proposal guidance from general knowledge, as AOSSIE has specific requirements that differ
  from standard GSoC norms.
---

# AOSSIE GSoC Proposal Writer & Reviewer

## Purpose

Help contributors write proposals that meet AOSSIE's actual standards — not generic GSoC advice.
Contributors commonly submit AI-generated, copy-pasted, or shallow proposals that ignore what
AOSSIE explicitly asks for. This skill prevents that.

**Two modes:**
- **HELPER** — contributor is writing from scratch or has a rough draft
- **REVIEWER** — contributor has a full draft and wants feedback before submitting

Detect mode from context. If unclear, ask: *"Do you want help writing your proposal, or do you
want me to review a draft you already have?"*

---

## What the Google Form Already Covers (DO NOT re-ask or re-generate these)

The AOSSIE GSoC Google Form collects these directly — the skill must focus ONLY on the
**Detailed Description PDF**:

- Personal info, social links, country
- Eligibility (age, conflicts of interest)
- Education and current study details
- PR history and AI tool usage
- Open source contributions outside AOSSIE
- Weekly timeline (Coding Weeks 8–22) — filled IN the form
- Summary (1–3 paragraphs) — filled IN the form
- Motivation — filled IN the form
- Tech stack overview — filled IN the form

**The Detailed Description PDF is where proposals fail or succeed.** That is this skill's focus.

---

## Mode: HELPER (Drafting the Proposal)

### Step 1 — Intake

Before writing anything, ask the contributor:

1. **Which AOSSIE project(s) are you proposing for?**
   (They can apply for more than one project(s) within the same org)
2. **What is your Discord username?**
3. **Do you have a PoC (Proof of Concept) repo ready?** If yes, share the link.
4. **Which mentor(s) did you work under in your previous PRs?**
5. **What is your proposed project(s) size?** (Preferably Large = 22 weeks)
6. **Highlight your most impactful PRs** with links — quality of contributions is prioritized over the number of PRs.
7. **Have you read the AOSSIE ideas list and identified a base idea + extension themes?**

Do not proceed to drafting until you have answers to at least 1, 2, 4, 5, and 6.

### Step 2 — Validate the Core Proposal Strategy

Before writing, check the proposal strategy against AOSSIE's 2026 AI-era guidance:

❌ **Weak proposal (will likely be rejected):**
> "I want to work on idea X. I've already started it. I'll complete it during GSoC."

✅ **Strong proposal:**
> "I want to work on idea X and theme T. I've made progress on X. I'll complete it and then
> propose novel ideas Y and Z aligned with theme T for the remaining GSoC time."

**Ask the contributor:** What are your Y and Z extensions? If they don't have any, help them
brainstorm based on the project(s)'s theme before continuing.

AOSSIE explicitly states: *"Having your own ideas is one way of standing out from the crowd."*
Proposals that only implement existing ideas without extensions show lack of innovation.

### Step 3 — Draft the Detailed Description PDF

Generate the PDF content in this structure (read `references/format-guide.md` for full specs):

1. **Header Block** — Title, project(s) size, Discord @, PoC link
2. **Abstract** — 1 paragraph, specific and technical
3. **Resume** — Brief, relevant only
4. **Table of Contents**
5. **Architecture Diagram** — mid-level, project(s)-specific (see format guide)
6. **Detailed Architecture Description**
7. **Challenges & Solutions** (optional but recommended)
8. **Packaging & Testing Plan**
9. **Future Expansion** — the Y and Z ideas
10. **Impactful PR Contributions** — links to high-quality PRs, with mentor names

### Step 4 — Run Self-Review Before Handing Back

After drafting, automatically run the REVIEWER checklist (see below) on the generated draft
and surface any gaps to the contributor before they treat it as done.

---

## Mode: REVIEWER (Checking an Existing Draft)

Load `references/checklist.md` and evaluate the draft section by section.

Return a structured review with:
- ✅ Pass / ⚠️ Weak / ❌ Fail per section
- Specific line-level feedback for anything ⚠️ or ❌
- A final readiness verdict: **Ready to Submit / Needs Work / Major Rework Required**

Always check against the bad patterns in `references/bad-patterns.md`.

---

## Hard Rules (Always Enforce)

1. **All proposals must be in English** — flag immediately if the draft has non-English content
2. **Title format:** `<project(s) Name>: <One sentence of what you will do>`
   - ❌ "My Proposal", "GSoC Proposal", "Proposal for AOSSIE"
   - ❌ Include your own name in the title
   - ✅ "Agora Blockchain: Implementation of new voting algorithms and zero-knowledge proofs"
3. **Mention mentor by name** under whom the contributor worked for previous PRs
4. **Link every PR** — do not just say "I have contributed PRs", list them
5. **PoC must exist or be committed to** — the form has a field for this; the PDF must reference it
6. **No generic architecture diagrams** — must be specific to the actual codebase
7. **Full 22-week justification** — every week of the coding period must be accounted for
8. **Extensions beyond base idea are expected** — especially if the base idea might be completed quickly

---

## Selection Criteria (Remind contributors of these explicitly)

Ranked by AOSSIE admin importance:
1. Quality of previous contributions to AOSSIE project(s) — quality and impact of PRs matter more than quantity
2. Feasibility of proposed project(s) within proposed timeline
3. Being a team player / willingness to be a long-term contributor
4. Genuine interest in the project(s)

Feedback on draft proposals is NOT a selection criterion — not getting mentor feedback on your
draft does not mean rejection.

---

## Reference Files

Read these when needed:

| File | When to read |
|------|-------------|
| [format-guide.md](https://raw.githubusercontent.com/kpj2006/proposal/main/references/format-guide.md) | When drafting or checking the detailed description structure |
| [checklist.md](https://raw.githubusercontent.com/kpj2006/proposal/main/references/checklist.md) | When reviewing a submitted draft |
| [bad-patterns.md](https://raw.githubusercontent.com/kpj2006/proposal/main/references/bad-patterns.md) | When contributor's draft shows signs of AI-dumping or shallow content |