# Common Bad Patterns in AOSSIE GSoC Proposals

These are the failure modes seen most often in AI-generated or low-effort proposals.
For each: identify the pattern, explain why it fails, show a fix.

---

## Pattern 1: The Generic Title

**What it looks like:**
- "My GSoC Proposal"
- "GSoC 2026 Application"
- "Proposal for AOSSIE"
- "John's Proposal for rein"

**Why it fails:**
Mentors review dozens of proposals. A non-informative title wastes their time and signals
the contributor didn't read the admin guidance.

**Fix:**
`rein: Replacing WebSocket and Nut.js with WebRTC and Koffi for cross-platform reliability`

---

## Pattern 2: The Idea-List Copy-Paste Abstract

**What it looks like:**
> "rein is a screen mirroring application. It allows users to mirror their device screens.
> I want to improve this application by adding new features and fixing existing issues."

**Why it fails:**
Zero technical specificity. Could have been written by someone who read the idea title for
5 seconds. Shows no understanding of the codebase.

**Fix:**
Name the specific components you're replacing, the specific problems they cause, the specific
technologies you're using, and one non-obvious challenge you'll face.

---

## Pattern 3: The "I'll Finish It" Proposal

**What it looks like:**
> "I have already implemented most of idea X. During GSoC I will complete the remaining work."

**Why it fails:**
If you'll be done in Week 3, what happens for the next 19 weeks? AOSSIE explicitly warns
against this in their 2026 guidance. Shows no forward thinking.

**Fix:**
> "I will complete idea X by Week 6. For the remaining 16 weeks, I propose to work on Y
> (aligned with the Communication theme) and Z (aligned with the Trust theme). Here is the
> technical justification for Y: ..."

---

## Pattern 4: The 3-Box Architecture Diagram

**What it looks like:**
A diagram with 3 boxes: "Frontend", "Backend", "Database" with arrows between them.
Or: a direct copy of the existing README diagram with no changes.

**Why it fails:**
Adds no information. Could describe any project(s). Mentors want to see WHAT YOU WILL BUILD,
not a generic system overview.

**Fix:**
Draw the specific components you are adding/modifying. Label protocols (WebRTC PeerConnection,
Koffi FFI bindings, IPC channels). Show NEW components in a different color. Reference the
existing CodeRabbit sequence diagrams from merged PRs for the right level of detail.

---

## Pattern 5: The Process-Challenge Challenges Section

**What it looks like:**
> Challenges:
> - Learning the new codebase will take time
> - Time management during the coding period
> - Communicating effectively with mentors

**Why it fails:**
These are not technical challenges. They are true for every contributor and every project(s).
They show you haven't thought about the actual engineering difficulty.

**Fix:**
> Challenges:
> - WebRTC NAT traversal in corporate/university networks will require a TURN server fallback.
>   The adaptive bitrate controller in the signaling layer handles this.
> - Koffi's Windows ARM64 support is incomplete as of v2.x; will need to test pre-release builds
>   and potentially vendor a patched version.

---

## Pattern 6: The Even Timeline

**What it looks like:**
Every week has exactly 2 tasks of equal size. Weeks are numbered but not differentiated.
No spikes for hard problems, no buffer weeks, no integration phases.

**Why it fails:**
Real project(s) don't work like this. An even timeline signals the contributor generated it
without thinking about actual implementation complexity.

**Fix:**
- Weeks 1–2: Spike on WebRTC P2P connection — this is highest-risk, do it first
- Week 3: Koffi integration for mouse/keyboard injection on Linux only
- Weeks 4–5: Extend Koffi to Windows and macOS, handle edge cases
- Week 6: Integration testing across platforms (buffer for unexpected issues)
- Week 7: PoC polish, video demo, start base idea documentation
...

---

## Pattern 7: No PR Links

**What it looks like:**
> "I have contributed 15 merged PRs to AOSSIE repositories."

**Why it fails:**
The #1 selection criterion is previous contributions. Without links, this claim is
unverifiable and appears inflated.

**Fix:**
```
Merged PRs:
- Fix race condition in duplicate PR detector — github.com/AOSSIE-Org/repo/pull/42 (Mentor: @mentor)
- Add OpenSSF Scorecard workflow — github.com/AOSSIE-Org/Template-Repo/pull/17 (Mentor: @admin)
```

---

## Pattern 8: Ignoring the PoC Requirement

**What it looks like:**
No PoC link in the header. Or: "I plan to create a PoC during the bonding period."

**Why it fails:**
The PoC is a hard requirement for many project(s). It demonstrates you can execute on the core
technical risk, not just write about it. Deferring it to the bonding period signals avoidance.

**Fix:**
Build a minimal PoC BEFORE final submission. For rein: show WebRTC + Koffi working on at least
one platform, with a video in the README. It doesn't have to be polished — it has to exist.

---

## Pattern 9: LLM Boilerplate Filler

**What it looks like:**
> "I am deeply passionate about open source and believe that collaborative development is the
> future of software. I am excited to contribute to AOSSIE's mission of..."

Or sections that could be copy-pasted into ANY proposal for ANY org.

**Why it fails:**
Mentors read hundreds of these. Boilerplate is instantly recognizable and wastes space that
should be used for technical content.

**Fix:**
Replace every generic sentence with something specific to THIS project(s), THIS codebase, or
THIS contributor's actual experience with AOSSIE.

---

## Pattern 10: Not Mentioning Mentor Names

**What it looks like:**
PRs are listed but mentor names are omitted. Or the proposal doesn't acknowledge which mentor
the contributor worked under.

**Why it fails:**
AOSSIE admins explicitly require this. It establishes context and lets reviewers cross-reference
with mentor feedback.

**Fix:**
In the PR list and in the intro section, mention: "I worked under mentor @name on project(s) X,
where I contributed Y."