# Authoring guide — how to architect a single skill

## Contents
- Progressive disclosure
- Degrees of freedom
- Scripting the deterministic parts
- Subagents and context management
- File-based handoff
- Reflection loops
- Naming and description
- When this is actually a multi-skill problem
- After building: evaluation is a different concern

This file is read by whichever subagent is doing the drafting or reviewing (Phase 3 onward in
`SKILL.md`). It's organized in two layers on purpose: the first five sections are durable design
principles that don't depend on any particular tool's mechanics; the *Subagents* section's
frontmatter details are Claude Code–specific and are the part most likely to drift if the platform
changes — treat that subsection as the one to re-verify against current docs if something here
stops matching reality.

## Progressive disclosure

A skill is read in layers, and each layer has a different cost:

1. **Metadata** (`name` + `description`) — preloaded for every skill, every session. This is the
   only part that's *always* in context, which is why the description carries the full weight of
   discovery (see *Naming and description*).
2. **SKILL.md body** — loaded only once the skill is judged relevant. Still costs tokens against
   the live conversation the moment it loads.
3. **Reference files, scripts** — loaded only if SKILL.md links to them and the task needs them.
   Zero cost otherwise, no matter how large.

The design consequence: **push everything that isn't needed on every invocation down a layer.**
SKILL.md is a table of contents with just enough body to handle the common case; anything
domain-specific, rarely needed, or purely reference material moves to a file SKILL.md links to.
The same rule governs prompts a skill writes at runtime, not just files it ships — see *the best
dispatch is "your turn."* in *Subagents and context management*.

Three shapes, pick by how the skill branches:

- **High-level guide with references** — one quick-start path in SKILL.md, deeper material
  (`FORMS.md`, `REFERENCE.md`, `EXAMPLES.md`) linked out. Use when there's one common path and a
  few less-common extensions.
- **Domain-specific split** — a reference file per domain (`reference/finance.md`,
  `reference/sales.md`) so a request about one domain never pulls in the others. Use when the
  skill covers several independent areas a single task will only touch one of.
- **Conditional details** — SKILL.md states the default inline, links out only for the harder
  branch ("simple edits: do X. For tracked changes, see REDLINING.md"). Use when there's a clear
  common case and a rare, heavier one.

Hard rules, because Claude reads skills by navigating the filesystem, not by ingesting the whole
directory:

- **Body under 500 lines.** Split before you hit it, not after.
- **One level deep.** Every reference file links directly from SKILL.md. A file only reachable by
  following a link from another reference file may get skimmed with `head -100` instead of read in
  full — information sitting past that second hop functionally doesn't exist.
- **Table of contents on any reference file over 100 lines**, so a partial read still shows the
  full shape of what's available.
- **Concise is the default, not a nice-to-have.** Every paragraph should answer "would Claude get
  this wrong without it?" A sentence explaining what a PDF is costs the same context as a sentence
  Claude actually needed — don't spend the shared budget on the first kind.

## Degrees of freedom

Match specificity to how fragile the step is — not to how important it is.

| Freedom | Form | When |
|---|---|---|
| High | Prose instructions | Multiple valid approaches; the right one depends on context a human would judge in the moment |
| Medium | Pseudocode / parameterized template | A preferred pattern exists but some variation is fine |
| Low | An exact script, run as-is | The operation is easy to get subtly wrong and consistency matters more than flexibility |

A narrow bridge over a cliff gets exact guardrails; an open field gets a heading and trust. Most
skills are a mix — the creative parts stay prose, the fragile parts become scripts (see next
section).

## Scripting the deterministic parts

**If the same input always produces the same correct output, it's a script, not an instruction.**
Parsing a file format, validating a schema, computing a value, checking a naming convention — none
of these benefit from being re-derived by an LLM on every run. They benefit from being solved once
and executed.

Rules for the scripts themselves:

- **Solve, don't defer.** Handle the foreseeable failure (file missing, permission denied,
  malformed input) with a specific message or a sane fallback — not a bare exception Claude has to
  interpret and route around every time.
- **No unexplained constants.** `TIMEOUT = 30  # HTTP calls typically finish well under this` is
  fine; `TIMEOUT = 47` is not, because nobody — including future-you — can tell if 47 is load-
  bearing or a typo.
- **Say whether Claude executes it or reads it.** "Run `validate.py`" and "see `validate.py` for
  the algorithm" are different instructions; a script bundled with neither is ambiguous.
- **Declare dependencies explicitly** rather than assuming a package is already installed.

Execution is preferred over having Claude regenerate the same code from scratch each time: it's
more reliable, it's deterministic, and the script's *output* is what costs tokens — not its
source, which never has to enter context at all.

**When the deterministic output is a whole file, not a value: template + render script, not a
prose code block.** A SKILL.md that says "write `eslint.config.js` with this content: ```js ...```"
makes Claude retype the same file body from prose every run — the same problem as any other
un-scripted deterministic step, just at file granularity. Instead, keep the canonical body as a
template file under `templates/` (or `assets/`), with placeholders for the parts that legitimately
vary per run (`{{project_name}}`, `{{researched_version}}`), and give the skill a script that
copies the template into the target location and substitutes the placeholders. SKILL.md then says
"run `scripts/render_template.py eslint.config.js --project foo`" instead of embedding the file.
This keeps the template's correctness fixed in one file (edit it once, every future run benefits)
and keeps SKILL.md's line count from ballooning with one code block per generated file.

## Subagents and context management

The decision isn't "should this skill use a subagent" in the abstract — it's **does this specific
phase pull in context this conversation doesn't need to keep.** Three shapes:

- **Rule-shaped** (must always happen, no judgment involved) → a script or a hook, not a subagent.
- **Knowledge-shaped** (Claude needs to know something to do the task) → the skill itself, or a
  reference file it loads.
- **Delegation-shaped** (work that *reads* or *writes* a lot of material — the artifact matters,
  the process doesn't need to stay visible) → a subagent. **Producing a file is delegation-shaped
  by definition**, draft or final, not only the wide reads that precede it.

Research, wide file reads before a refactor, fetching several external sources, and every phase
that emits an artifact — all delegation-shaped. A single trivial lookup or a 20-line edit is not;
spinning up a subagent for it is overhead that protects nothing (checklist item N5).

**Keep the orchestrator thin.** It holds the big picture and spends its context on decisions, not
on material. What comes back from a subagent is a summary, a path, or a routing list — never
content (mechanics in *File-based handoff* below).

The failure this prevents isn't reading too much. It's a skill whose main flow drafts the artifact
inline and then spawns a subagent to *review* it — that delegates the cheap half and keeps the
expensive one. The draft is now in the orchestrator's context, so every later round of fixes is
paid at full price. **Delegate the producing, not just the checking.** The generator is a subagent
too, and the orchestrating turn should be left holding a path and a line count.

**A subagent's prompt states what it returns, and bounds it.** Name the shape and cap the size —
"the path plus a one-line summary", "counts plus failing item ids plus the files they name", "at
most 12 lines". A subagent left to decide what to report will paste its work back.

**A dispatch names three things: where to get the input, what to do, and where to put the output.**
Nothing else needs to travel. Inputs and outputs are paths, never inlined content (mechanics and
the file-naming convention in *File-based handoff*), and the "what to do" can be as small as naming
the skill the subagent should run, when that skill already encodes its own inputs and outputs. What
comes back is a summary plus the location of what was produced.

**The orchestrator holds a manifest, not material.** Its running state across phases is a list of
what exists and where — one line and a path each. That manifest is what makes the next dispatch
writable without reopening anything, and it is the only state that has to survive between phases.

**The best dispatch is "your turn."** The more a subagent's own skill or reference file encodes
where its input lives and where its output goes, the less the orchestrator has to say. A dispatch
that has grown long with instructions about inputs and outputs is the same defect as a bloated
SKILL.md — knowledge sitting a layer above the place that needs it — and it takes the same fix, for
the same reason: push it down into a file the subagent loads itself (*Progressive disclosure*).

**Two independent levers, and they compose:**

1. **The whole skill runs isolated.** Set `context: fork` in the skill's own frontmatter. The
   skill's body becomes the subagent's prompt, it runs with no access to the calling conversation's
   history, and — by default — in the background, with its result arriving when it's done. Add
   `agent: Explore` (or `Plan`, or a custom agent from `.claude/agents/`) to pick what tools and
   system prompt it runs with; omitting `agent` uses `general-purpose`. Set `background: false`
   only if the very next step in the calling conversation depends on this skill's result, or if the
   skill needs a tool outside the narrower set background subagents get. `context: fork` only makes
   sense when the skill's body is an actual task ("Research $ARGUMENTS...") — a skill that's really
   just reference guidance ("follow these API conventions") has nothing for the forked subagent to
   *do*, and it returns without meaningful output.
2. **Individual phases inside the skill fan out.** The skill's own instructions launch subagents
   for specific heavy phases (via the `Agent` tool) while the orchestrating turn stays cheap. This
   is the shape to reach for when a skill has 2+ phases that each read or write substantial
   material, or independent work that can run in parallel — the orchestrator dispatches, each
   subagent does its phase against its own context, and only compact results come back.

   **Which phases delegate is decided by volume, not by importance.** A phase can be creative,
   judgment-heavy and central to the skill and still be delegation-shaped — the creative ones
   usually are, precisely because their output is long. The line: a phase that writes a file, or
   reads more than a screenful, delegates; a phase whose whole cost is a lookup, a small edit, or a
   decision made from results already in hand stays inline. That line is also where N5 applies — a
   subagent below it protects no context and is pure overhead, and a phase above it that stays
   inline poisons the orchestrator for the rest of the run. Judge the volume, and only the volume,
   to know which rule you're under.

Use lever 1 when the *entire* skill is disposable-context work end to end. Use lever 2 when the
skill has a mix — some orchestration logic that should stay visible, plus one or more heavy phases
that shouldn't. They compose: a forked skill can itself launch further subagents for its phases.

Permission hygiene applies either way: scope a subagent's tools to what its phase actually needs.
A research phase gets read/search/web tools; a phase that writes the final artifact gets
write/edit. Granting everything by default defeats the isolation the subagent was for.

## File-based handoff

Once work is delegated, it has to come back — and the mechanism for that matters as much as the
decision to delegate at all.

- **Write the artifact to a path, hand the path, not the content.** A generator subagent writes
  its draft to disk and reports the path plus a one-line summary; it does not paste the draft back
  into its response for the orchestrator to relay. The orchestrator's context stays flat regardless
  of how large the draft is.
- **Compact handoffs.** When what needs to move between subagents *is* meant to sit in context
  (not the deliverable itself, but coordination data — a spec, a list of findings, a status), keep
  it short — structured and skimmable, not a transcript.
- **Name handoff files for what they are and who's involved**, e.g.
  `.cache/<skill-name>/spec-<slug>.md`, `.cache/<skill-name>/review-r<round>.md`. A reader should
  be able to tell from the filename alone what's in it and when it was produced.
- **The receiving subagent is told the exact path to read**, not "check the cache directory" —
  ambiguity here is where handoffs silently fail.
- **The full artifact is read exactly once more than necessary: never.** If the orchestrator only
  needs to know pass/fail and a short reason, that's what the subagent returns — it doesn't dump
  the artifact into its response just because it has it. Enforce this at launch, not at read time:
  the prompt names the return shape and its cap (see the return contract above), because a subagent
  that wasn't told what to return decides for itself, and it decides "all of it".

## Reflection loops

Not every skill needs one. Reach for a generate → review loop when the output is creative,
quality-critical, or has a real failure mode a first pass is likely to hit — a design document, a
generated skill, a piece of content whose defects aren't obvious from a glance. Skip it for
mechanical, low-stakes output where a script or a simple check already catches what could go
wrong; a reflection loop bolted onto something that's never actually wrong is pure latency.

When it's warranted:

- **Generator and reviewer are different subagents, not the same one asked to "check its own
  work."** A model reviewing its own immediately-prior output tends to defend it, because the
  context that produced the flaw is still influencing the judgment of it. A second subagent,
  spawned fresh, with only the artifact and the checklist, has nothing to defend.
- **The reviewer works from first principles, not from a summary of the generator's reasoning.**
  Its job is to independently re-derive whether the artifact is good against the shared checklist
  — not to grade the generator's stated intentions. Never hand the reviewer the generator's
  rationale before it scores.
- **Findings cite specifics.** A finding names the checklist item it fails and points at a
  location — file, line, section. "Doesn't feel complete" is not a finding a generator can act on.
- **State the pass bar up front.** For structural/correctness gates (like `checklist.md`), every
  item must pass — there's no partial credit for a broken reference link. For genuinely creative
  output where some subjectivity is real, a numeric threshold (e.g. ≥90%) can be appropriate — but
  default to all-must-pass unless there's a specific reason a percentage makes more sense.
- **Cap the rounds.** Two to three is typical. A finding that survives two revisions is usually not
  a defect anymore — it's a disagreement worth surfacing to the user rather than looping on.
  Uncapped reflection is a cost problem waiting to happen, not a quality guarantee.
- **PASS has to be a real, reachable verdict.** If a reviewer run against a genuinely solid draft
  can't produce a clean pass, the checklist is miscalibrated, not the draft. A reviewer that always
  finds *something* to flag isn't adding signal.
- **Before trusting the loop, sanity-check the checklist itself**: would it actually fail a bad
  draft? See the *Sanity check* section of `checklist.md`. A reflection loop is only as strong as
  its rubric's ability to discriminate.

## Naming and description

- **Name**: lowercase letters, numbers, hyphens only, ≤64 characters, no "anthropic" or "claude" in
  it. Name the activity plainly (`processing-pdfs`, `pdf-processing`, `skill-architect`) — gerund
  or noun-phrase form are both fine; vague names (`helper`, `utils`, `tools`) are not.
- **Description**: third person, always. States both *what* the skill does and *when* to use it,
  and includes the actual words a user would type or say — this field is what Claude matches
  against a live request among potentially 100+ skills, so specificity here is the highest-leverage
  sentence in the whole file. "Processes Excel files and generates reports. Use when analyzing
  spreadsheets or .xlsx files." beats "Helps with documents" or "I can help you with Excel."

## When this is actually a multi-skill problem

Some signs the request isn't for one skill's architecture but for a *set* of skills — timelines
that don't match (something daily next to something quarterly), a mix of strategic decision-making
and operational execution, five or more genuinely distinct user-triggered actions. If those show
up during intake, say so and point at a plugin-decomposition tool rather than forcing the whole
thing into one oversized SKILL.md. This guide only covers getting one skill's internals right.

## After building: evaluation is a different concern

Everything above is about **architectural** correctness — checkable at design time, from the files
on disk. It says nothing about whether the finished skill actually triggers on the right prompts or
performs well when it does; that's a **behavioral** question, answered by running the skill for
real against representative prompts, with and without it available, and comparing. That's a
distinct, longer-running loop worth doing after the architecture is sound — not a substitute for
it, and not something this guide re-derives from scratch when tooling for exactly that purpose may
already be available in the environment.
