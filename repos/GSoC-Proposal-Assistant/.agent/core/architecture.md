# GSoC Proposal Assistant — Workflow Architecture

## Overview Architecture

The GSoC Proposal Assistant operates across two primary execution pipelines:

```
                          ┌───────────────────────────┐
                          │   Contributor Query/Draft  │
                          └─────────────┬─────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                 [ HELPER MODE ]               [ REVIEWER MODE ]
            (Drafting From Scratch)        (Evaluating Existing Draft)
                         │                             │
       ┌─────────────────┴─────────────────┐           │
       ▼                                   ▼           ▼
1. Intake Information               1. Validate Y & Z  1. Load Checklist
2. Strategy Validation                 Novel Ideas     2. Audit Bad Patterns
3. Generate PDF Structure           2. Review PDF      3. Score Sections
4. Self-Review Checklist               Format          4. Output Verdict
```

---

## HELPER Pipeline (4 Steps)

1. **Intake Phase**: Collect project choice, Discord handle, mentor names, PoC repo link, and impactful PR links.
2. **Strategy Validation**: Ensure candidate has proposed novel extension themes (Y & Z ideas) beyond the base idea.
3. **Drafting Phase**: Format the 10-section Detailed Description PDF according to [format-guide.md](../instructions/format-guide.md).
4. **Self-Review**: Run the 6-block reviewer checklist against the drafted document.

---

## REVIEWER Pipeline (3 Steps)

1. **Checklist Audit**: Evaluate draft against [checklist.md](../instructions/checklist.md) (Blocks 0 through 5).
2. **Anti-Pattern Check**: Scan for red flags in [bad-patterns.md](../instructions/bad-patterns.md).
3. **Structured Scoring Output**: Output section scores (✅ Pass / ⚠️ Weak / ❌ Fail) and final verdict (**Ready to Submit**, **Needs Work**, **Major Rework Required**).
