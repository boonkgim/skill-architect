---
name: skill-architect
description: Create a new Claude Code skill or improve an existing one, designing its internal architecture — progressive disclosure, scripted deterministic steps, subagent delegation, file-based handoff between subagents, and a generate/review reflection loop when the output is quality-critical — then validates it against a concrete checklist. Use when the user asks to create a skill, turn a repeated procedure into a skill, write a SKILL.md, or review/improve an existing skill's structure.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch
---

# Creating Skills — Author or Improve a Single Skill's Architecture

Designs and builds **one skill's internals** well. It does not decide whether a request should
become several skills (a plugin-decomposition question — see *Scope check* below), and it does
not run behavioral evaluations after the skill exists (a different, longer-running concern — see
Phase 7).

Two reference files carry the actual design knowledge and are read by subagents, not by this
orchestrator inline — keep this file itself a table of contents, per its own advice:

- [reference/authoring-guide.md](reference/authoring-guide.md) — how to design progressive
  disclosure, scripts, subagent delegation, file handoff, and reflection loops.
- [reference/checklist.md](reference/checklist.md) — the shared DO/DON'T quality gate used by
  both the generator and the reviewer.

---

## Parse mode

```
"create <description>"  → Mode 1: Create
"improve <path>"        → Mode 2: Improve
ambiguous or unclear    → Ask: "Create a new skill, or improve an existing one?"
```

---

## Scope check (both modes)

Before anything else, check whether this is really a single skill. Signs it isn't:

- The actions described span clearly different cadences (something daily next to something
  quarterly or one-time).
- The work mixes strategic decision-making (positioning, planning) with operational execution
  (production, delivery) in a way that would force one SKILL.md to do both.
- Five or more genuinely distinct user-triggered actions are being described at once.

If any of these show up, say so and ask whether the user wants a multi-skill plugin instead — if
a plugin-decomposition tool is available in this environment, name it. Otherwise continue: this
skill only architects one skill's internals, and forcing a plugin-shaped request into one
oversized SKILL.md produces exactly the kind of file this skill exists to prevent.

---

## Mode 1: Create

### Phase 1: Intake

Gather, asking only what can't be inferred:

| Field | Notes |
|---|---|
| One-sentence purpose | What does invoking this skill actually do? |
| Trigger terms | What would the user type or say that should surface this skill? |
| Target scope | Personal (`~/.claude/skills`), project (`.claude/skills` in the current repo), or plugin. Ask via `AskUserQuestion` if not stated — this has real consequences (shared via git vs. available everywhere) and isn't inferable. |
| Name | Propose a candidate that names the activity plainly (`processing-x` or `x-processing`); confirm with the user rather than asking open-ended. |
| Inputs / outputs | What does it read, what does it produce or change? |

If a similar skill already exists in the target scope, read it first and match its conventions
rather than inventing new ones — consistency across a skill collection is itself a quality
property.

### Phase 2: Research (only if the domain needs it)

If the skill's subject matter requires current, specific knowledge this conversation doesn't
already have (an API's conventions, a domain's best practices, a library's current version),
delegate the lookup to a subagent rather than doing it inline — this is delegation-shaped work per
*Subagents and context management* in the authoring guide. Have it write findings to
`.cache/skill-architect/research-<slug>.md` and return only a short summary. Skip this phase
entirely for skills that don't need external knowledge.

### Phase 3: Architecture design

Read `reference/authoring-guide.md`. Walk through its sections in order and settle, for this
specific skill:

1. **Progressive disclosure plan** — what lives in SKILL.md vs. reference files vs. scripts, and
   which of the three shapes (high-level+refs, domain split, conditional details) fits.
2. **Deterministic-step audit** — list every step that always produces the same output for the
   same input. Each becomes a script, named and placed under `scripts/`.
3. **Subagent audit** — does any phase of *this skill*, once built, pull in heavy disposable
   context (research, wide reads, a large first draft)? If the whole skill is that shape end to
   end, it gets `context: fork` in its own frontmatter. If only specific phases are, the skill's
   instructions launch `Agent`-tool subagents for just those phases. If neither applies, say so —
   not every skill needs this.
4. **File-handoff design** — if Phase 3.3 introduced any subagents, name the handoff files now
   (`.cache/<new-skill-name>/...`) and what each one carries.
5. **Reflection-loop decision** — is this skill's own output quality-critical, creative, or easy
   to get subtly wrong? If yes, design a generator/reviewer split for *the new skill itself* using
   the same pattern this meta-skill uses on itself (Phase 5 below) — a shared checklist specific to
   that skill's domain, pass bar, and round cap. If the output is mechanical and low-stakes, skip
   it and say why.

Write the settled design as a compact spec to `.cache/skill-architect/spec-<slug>.md`. This is the
file handoff for Phase 4 — don't carry the design forward as conversation state when a subagent is
about to do the writing.

### Phase 4: Generate

- **Simple case** (no research phase ran, design fits in a small SKILL.md, no reference files):
  write the files directly with `Write`. Spinning up a subagent here would be delegation with
  nothing to protect (checklist item N5).
- **Otherwise**: launch a `general-purpose` subagent with the `Agent` tool. Hand it the spec file
  path, the `reference/authoring-guide.md` path, and the `reference/checklist.md` path — not their
  contents inlined into the prompt. Instruct it to write every file (`SKILL.md`, any
  `reference/*.md`, any `scripts/*`) to the target scope directory and return a short summary: files
  written, line counts, and one line per design decision from Phase 3. The orchestrator's context
  never holds the full generated content.

### Phase 5: Reflection loop (only if Phase 3.5 decided yes)

Launch a **separate** `general-purpose` subagent as reviewer. It receives only:

- The path to the generated skill's directory.
- The path to `reference/checklist.md`.

Not the spec file, not the generator's summary, not this conversation. It scores every DO/DON'T
item PASS/FAIL/N/A against the files on disk and returns specific findings — checklist item
number, file, line or section, one line on what to change. No vague findings.

Triage the results yourself:

- Any FAIL → send the specific findings (not the whole checklist again) to a reviser subagent
  (can be a fresh `general-purpose` agent, or the generator continuing) to fix in place.
- Re-run the reviewer. **Cap at 3 rounds.** A finding surviving two revisions is more likely a
  design disagreement than a defect — stop and surface it to the user instead of looping.
- All PASS/N/A → done. A clean pass is the expected outcome by round two, not a rare event — if
  the reviewer can't produce one against a genuinely solid draft, the checklist itself needs
  fixing (see *Sanity check* in `checklist.md`), not the draft.

### Phase 6: Validate

Run the deterministic checker against the generated skill:

```bash
python3 <this-skill-dir>/scripts/validate_skill.py <path-to-new-skill-dir>
```

Fix every `FAIL` before reporting done. `WARN`s are judgment calls — fix them or note why not.

### Phase 7: Summary

Report:

- File tree of what was created.
- Which steps were scripted vs. subagent-delegated vs. written directly, and why (one line each).
- Whether a reflection loop ran, how many rounds, and the final verdict.
- The `validate_skill.py` result.
- **What this didn't do**: this skill checked architecture, not behavior. Whether the new skill
  actually triggers on the right prompts and performs well when it does is a separate, longer-
  running question — answered by running it for real against representative prompts, with and
  without it available, and comparing. If evaluation tooling for exactly that purpose is available
  in this environment, name it as the next step rather than re-deriving an evaluation harness here.

---

## Mode 2: Improve

Same architecture lens, run against an existing skill instead of a fresh design.

1. **Read the target.** The skill's `SKILL.md` and every file it links to (one level deep, per the
   authoring guide — that's the same rule this skill enforces on others).
2. **Validate.** Run `scripts/validate_skill.py` against it first — fix anything mechanical
   (broken links, missing TOC, frontmatter issues) before spending a reflection round on it.
3. **Review.** Run the same reviewer step as Phase 5 above: a fresh subagent, given only the
   skill's files and `reference/checklist.md`, scoring independently. This is the skill's own
   dogfood case — the reviewer must not have participated in writing the skill being reviewed.
4. **Show the findings to the user before changing anything.** This is someone else's skill (or a
   past version of this conversation's own work) — don't silently rewrite it. Present the FAILs,
   ask which to apply.
5. **Apply agreed fixes**, re-run `validate_skill.py`, report the before/after.
