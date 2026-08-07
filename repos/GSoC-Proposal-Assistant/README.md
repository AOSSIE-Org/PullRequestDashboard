# AOSSIE GSoC Proposal Assistant

Open with: 

[![Claude](https://img.shields.io/badge/Claude-d97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/new?q=Read%20your%20full%20instructions%20from%20these%20links%3A%0A1.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/SKILL.md%0A2.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/format-guide.md%0A3.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/checklist.md%0A4.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/bad-patterns.md%0A%0AThen%20ask%20me%20whether%20I%20want%20help%20writing%20my%20proposal%20from%20scratch%20%28HELPER%20mode%29%20or%20if%20I%20have%20a%20draft%20ready%20for%20review%20%28REVIEWER%20mode%29.)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)](https://chatgpt.com/?q=Read%20your%20full%20instructions%20from%20these%20links%3A%0A1.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/SKILL.md%0A2.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/format-guide.md%0A3.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/checklist.md%0A4.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/bad-patterns.md%0A%0AThen%20ask%20me%20whether%20I%20want%20help%20writing%20my%20proposal%20from%20scratch%20%28HELPER%20mode%29%20or%20if%20I%20have%20a%20draft%20ready%20for%20review%20%28REVIEWER%20mode%29.)
[![Perplexity](https://img.shields.io/badge/Perplexity-20B2AA?style=for-the-badge&logo=perplexity&logoColor=white)](https://www.perplexity.ai/search?q=Read%20your%20full%20instructions%20from%20these%20links%3A%0A1.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/SKILL.md%0A2.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/format-guide.md%0A3.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/checklist.md%0A4.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/bad-patterns.md%0A%0AThen%20ask%20me%20whether%20I%20want%20help%20writing%20my%20proposal%20from%20scratch%20%28HELPER%20mode%29%20or%20if%20I%20have%20a%20draft%20ready%20for%20review%20%28REVIEWER%20mode%29.)
[![Grok](https://img.shields.io/badge/Grok-000000?style=for-the-badge&logo=x&logoColor=white)](https://grok.com/?q=Read%20your%20full%20instructions%20from%20these%20links%3A%0A1.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/SKILL.md%0A2.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/format-guide.md%0A3.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/checklist.md%0A4.%20https%3A//raw.githubusercontent.com/kpj2006/proposal/main/references/bad-patterns.md%0A%0AThen%20ask%20me%20whether%20I%20want%20help%20writing%20my%20proposal%20from%20scratch%20%28HELPER%20mode%29%20or%20if%20I%20have%20a%20draft%20ready%20for%20review%20%28REVIEWER%20mode%29.)

---

## Two Ways to Use

The assistant works in two distinct modes depending on your progress:

1.  **HELPER Mode:** If you are just starting or have a rough outline. The AI will ask you questions (project names, PR history, PoC links) to help you build a solid structured proposal from scratch.
2.  **REVIEWER Mode:** If you already have a full draft. Paste your draft, and the AI will check it against AOSSIE's 2026 standards, giving you a structured review (Pass/Weak/Fail) and specific line-level feedback.

---

## Full Flow (zero infra)

```
contributor opens your GitHub repo
        ↓
clicks one of the 'Open with' links in README
        ↓
The LLM fetches SKILL.md and references from raw GitHub URLs
        ↓
The LLM asks: "Do you want help writing your proposal or do you want me to review a draft?"
        ↓
contributor proceeds with drafting or pasting draft
        ↓
done
```
