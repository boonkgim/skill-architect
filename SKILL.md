---
name: skill-architect
description: Creates a new Claude Code skill or improves an existing one, designing its internal architecture — progressive disclosure, scripted deterministic steps, subagent delegation, file-based handoff between subagents, and a generate/review reflection loop when the output is quality-critical — then validates it against a concrete checklist. Use when the user asks to create a skill, turn a repeated procedure into a skill, write a SKILL.md, or review/improve an existing skill's structure.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch
---

# Creating Skills — Author or Improve a Single Skill's Architecture

Designs and builds **one skill's internals** well. It does not decide whether a request should
become several skills (a plugin-decomposition question — see *Scope check* below), and it does
not run behavioral evaluations after the skill exists (a different, longer-running concern — see
Phase 7).

Two reference files carry the actual design knowledge — keep this file itself a table of contents,
per its own advice:

- [reference/authoring-guide.md](reference/authoring-guide.md) — how to design progressive
  disclosure, scripts, subagent delegation, file handoff, and reflection loops. You read this once,
  at Phase 3, because the design decisions are what the user gets to object to; the generator
  subagent reads it again from the path.
- [reference/checklist.md](reference/checklist.md) — the shared DO/DON'T quality gate used by
  both the generator and the reviewer. **You never read this file** — it is scored by subagents
  against files on disk, and an orchestrator holding the rubric starts scoring in its own head.

---

## Context budget — read this before either mode

This skill's own failure mode is the one it exists to prevent: a run that writes a skill cheaply,
then spends the whole context window *reviewing and repairing* it by hand. One principle governs
both modes, and the rules below are its consequences.

**The orchestrator is thin.** Its job is to hold the big picture — the design, the phase, the
routing — and to spend its context on decisions, not on material. Every phase that touches volume,
whether it reads, drafts, reviews or fixes, belongs to a subagent; what comes back is a summary, a
path, or a routing list, never the material itself.

- **Never pull material back into this turn.** Three forms, each with its own reason:
  - **You never read a skill's source.** Not the one being generated, not the one being improved.
    Subagents read files; you hold paths, counts and decisions.
  - **You never read a review report.** The reviewer writes findings to a file and returns a summary
    short enough to show the user. The fixers read the file. This is the leak that costs the most,
    because it costs twice — once to read the report, once to read every file it names.
  - **You never apply a fix to a generated file.** Every FAIL routes to a subagent that owns one file.
- **Delegate the producing, not just the checking.** The recurring failure is not reading too much —
  it is an orchestrator that drafts the artifact itself and then spawns a subagent to review it.
  That delegates the cheap half and keeps the expensive one: the draft is already in context, so
  every later round of fixes is paid for at full price. The generator is a subagent too. If a phase
  produces a file, it is delegation-shaped, and the only thing the orchestrating turn should hold
  afterwards is the path and a line count.
- **A dispatch names three things: where to get the input, what to do, and where to put the
  output.** Nothing else needs to travel. Inputs and outputs are paths; the task may be as small as
  naming the skill that already encodes its own inputs and outputs. What comes back is a summary
  plus the location of what was produced.
- **State the return contract when you dispatch, and bound it.** Every subagent prompt names exactly
  what to return and caps its size — "files written with line counts", "counts plus failing item ids
  plus the files they name", "at most 12 lines". A subagent left to decide what to report will paste
  its work back, and by then the context is already spent.
- **You hold a manifest, not material.** Your running state is the list of what exists and where —
  one line and a path each. That manifest is the whole reason the next dispatch is writable without
  reopening anything, and it is the only thing that has to survive between phases.
- **The best dispatch is "your turn."** The more a subagent's own skill or reference file already
  encodes where its input lives and where its output goes, the less you have to say. A dispatch that
  has grown long with instructions about inputs and outputs is telling you that knowledge belongs one
  layer down, in a file the subagent loads itself — push it there rather than restating it on every
  run.
- **The orchestrator's own tool calls are part of its budget.** A wide grep or a full-file read in
  the orchestrating turn defeats delegation exactly as thoroughly as a chatty subagent does.

Each phase below states what it may leave in your context. If a step would blow that, delegate it —
the skill on disk is the deliverable, not the transcript of making it.

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
`.cache/skill-architect/research-<slug>.md` and to return **at most 8 lines: that file's path, then
one line per finding that changes a design decision** — no quotes, no source dumps. Skip this phase
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
   that skill's domain, pass bar, round cap, **the path its reviewer writes findings to, and the
   per-file fixer fan-out that reads them** (checklist D18/D19). A loop designed without that last
   part gets repaired by hand by whatever context invokes it, which is where a delegated build
   quietly gives its context saving back. If the output is mechanical and low-stakes, skip it and
   say why.

Record the outcome as a **decision list, not a document**: write
`.cache/skill-architect/spec-<slug>.md` as **at most 8 lines — one line per decision from the five
sub-steps above, plus the skill's name and its target directory**, each line naming the choice and
the path it implies. This is the file handoff for Phase 4 — don't carry the design forward as
conversation state when a subagent is about to do the writing.

These decisions stay yours because architecture is the big picture and delegating it would leave you
routing a design you never made. What does not stay yours is prose about them: a line per decision is
manifest, a paragraph explaining one is material, and material belongs to whoever writes the file —
the Phase 4 generator expands these lines into a body, so anything you draft here you draft twice.
This is the only file the orchestrating turn writes itself, and 8 lines is why that holds: it is the
reference to the artifact, not the artifact, and dispatching a subagent to transcribe eight decisions
it didn't make would be delegation that protects nothing (checklist N5). If the list won't fit in 8
lines, the overflow is the generator's to write, not yours.

### Phase 4: Generate

**Delegate by default.** Launch a `general-purpose` subagent with the `Agent` tool. Hand it the spec
file path, the `reference/authoring-guide.md` path, the `reference/checklist.md` path, and — if
Phase 2 ran — the `.cache/skill-architect/research-<slug>.md` path, not their contents inlined into
the prompt. Instruct it to write every file (`SKILL.md`, any
`reference/*.md`, any `scripts/*`) to the target scope directory and to **return at most 12 lines:
each file written with its line count, then one line per design decision from Phase 3** — no
excerpts, no rationale prose. The orchestrator's context never holds the full generated content.

**The test is the volume the phase produces, not how hard the thinking was.** An earlier version of
this phase let you write the files yourself whenever the design was "simple" — small SKILL.md, no
research, no reference files — on the grounds that a subagent would have nothing to protect
(checklist item N5). That threshold measured the wrong thing: writing a 200-line SKILL.md costs you
200 lines whether the design took five minutes or an hour, and those lines then sit in context for
every review round and every fix that follows.

**The exception is narrow**: a single file that is frontmatter and nothing else, or a one-line edit
to a file that already exists. Below that bar the dispatch genuinely costs more than the write, which
is N5's real case — a subagent spawned to do a 20-line edit protects nothing — and N5 still stands
for it. Anything that produces a body, delegate.

### Phase 5: Reflection loop (only if Phase 3.5 decided yes)

Launch a **separate** `general-purpose` subagent as reviewer. It receives only:

- The path to the generated skill's directory.
- The path to `reference/checklist.md`.

Not the spec file, not the generator's summary, not this conversation.

It scores every DO/DON'T item PASS/FAIL/N/A against the files on disk and **writes the findings to
`.cache/skill-architect/review-<slug>-r<round>.md`** — one line each: checklist item number, file,
line or section, and what to change. No vague findings.

It returns to you **at most 20 lines**, and only this:

- the counts (`n PASS / n FAIL / n N/A`);
- each failing item number with a clause of ten words or so — enough to show the user, not enough
  to fix from;
- **the list of files those findings name.** That last part is what lets you route fixes without
  reading the findings file yourself.

**Fix by delegation.** Launch one reviser subagent per file in that list, **all in a single
message**, each given: the findings file's path, the one file it owns, and
`reference/checklist.md`'s path. It reads the findings itself and fixes in place, and **returns one
line: its file plus the item numbers it closed** — never a diff, because a diff is the material
coming back. Pulling the report into this conversation and editing the files by hand costs more
context than generating the skill did — that is the specific leak this phase exists to prevent, and
it is the one this skill has historically lost runs to.

One exception, because no single file owns them — **cross-file findings**: D3 (body over 500
lines, so something has to move out), D4 and N3 (a reference file linked two hops deep, or linked
from nothing), and D12–D14 (the reflection loop the *generated* skill defines, which spans its
SKILL.md and its own checklist). Send those to a single structure-fixer subagent that owns the
whole skill directory — still reading the report from disk, still returning one line per item it
closed, still not through you.

Then:

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

1. **Map the target — don't read it.** Launch one `Explore` subagent. It reads the skill's
   `SKILL.md` and every file linked one level deep, and writes
   `.cache/skill-architect/map-<slug>.md`, **≤40 lines**: the file tree with line counts, one line
   on what each file is for, the phases SKILL.md defines, and where it already delegates. It
   **returns at most 3 lines: the map file's path, the skill's total line count across all files,
   and the number of files it linked** — the map is read from disk, not pasted back, or the return
   becomes a second copy of the thing you delegated. You read that map. Reading a mature skill and
   its references directly is 1,500 lines before the review has even started — and the reviewer is
   going to read the real files anyway.
2. **Validate.** Run `scripts/validate_skill.py` against it — fix anything mechanical (broken
   links, missing TOC, frontmatter issues) before spending a reflection round on it. Its output is
   short and specific, so this one is yours to act on directly.
3. **Review.** Run the same reviewer step as Phase 5 above, with the same file handoff: findings to
   `.cache/skill-architect/review-<slug>-r<round>.md`, and the same bounded return — **≤20 lines:
   counts, failing item ids with a ten-word clause each, and the list of files they name**. A fresh
   subagent, given only the skill's directory path and `reference/checklist.md`.
   This is the skill's own dogfood case — the reviewer must not have participated in writing the
   skill being reviewed.
4. **Show the findings to the user before changing anything.** This is someone else's skill (or a
   past version of this conversation's own work) — don't silently rewrite it. Present the returned
   failing items and the findings file's path, so anyone who wants the full reasoning opens the
   file. Ask which to apply. Do not paste the file into the conversation to make it easier to read
   — that is the whole saving, handed back at the last step.
5. **Apply agreed fixes by delegation** — the same one-subagent-per-file fan-out as Phase 5, each
   told which item numbers the user approved and which to leave alone, and each **returning one
   line: its file plus the items it closed or declined**. Then re-run `validate_skill.py` and report
   the before/after.
