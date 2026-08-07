# Skill quality gate — the shared checklist

## Contents
- How this file is used
- DO — 22 items, D1–D22
- DON'T — 12 items, N1–N12
- Sanity check before relying on this checklist

This is the **one shared rubric** both the generator and the reviewer work against in the
reflection loop (Phase 5 of `SKILL.md`). The generator treats it as a target; the reviewer treats
it as an independent scoring sheet. Neither role rewrites this file mid-review — a moving target
defeats the point of a shared gate.

Every item below is written to be **checkable**, not a matter of taste. "Is this well organized?"
is not on this list — "does every reference file link directly from SKILL.md, not through another
reference file?" is. A finding that can't point at a specific line is not a finding.

## How this file is used

- **Generator**: build the skill so every DO item is true and no DON'T item applies. Note in the
  handoff summary any item that's deliberately N/A and why (e.g. "no scripts — nothing in this
  skill is deterministic").
- **Reviewer**: score every item PASS / FAIL / N/A against the artifact **only** — the files on
  disk, plus this checklist. Not the generator's rationale, not the conversation that requested
  the skill. A reviewer who reads the generator's justification before scoring will rubber-stamp
  it instead of re-deriving the judgment; that's the whole reason the two roles are separate
  subagents with separate context.
- **Pass bar**: every DO/DON'T item scores PASS or N/A. A single FAIL blocks — this is a
  structural-correctness gate, not a creative-quality one, so there's no "≥90% is good enough."

## DO

| # | Item |
|---|---|
| D1 | `description` is third person, states both what the skill does and when to use it, and includes the specific terms a user would type or say |
| D2 | `name` is lowercase letters/numbers/hyphens only, ≤64 chars, names the activity plainly (not a vague `helper`/`utils`/`tools`) |
| D3 | SKILL.md body is under 500 lines; anything longer is split into reference files |
| D4 | Every reference file is linked **directly** from SKILL.md — no file only reachable by following a link from another reference file |
| D5 | Any reference file over 100 lines opens with a `## Contents` section |
| D6 | Every deterministic step (same input → same output, every time) is a script, not an LLM instruction asking Claude to "calculate," "parse," or "generate" something mechanical |
| D7 | Scripts handle their own errors and provide a fallback or a specific actionable message — never a bare exception left for Claude to interpret |
| D8 | Every constant in a script is justified by an adjacent comment — no unexplained numbers |
| D9 | Any phase that would pull heavy, disposable context into the conversation (research, reading many files, a large draft) runs in a subagent, not inline |
| D10 | Work handed from one subagent to another goes through a file on disk, and the receiving side is told the exact path to read — not returned as text and carried onward through the conversation. **Scope: the handoff medium.** D10 asks whether the work exists as a file at all and whether the next agent is pointed at it; what the orchestrator's dispatch prompt then *carries* — a path or a body — is D22's. A dispatch that pastes a file's contents instead of its path is one defect and scores FAIL on D22 alone, not on both |
| D11 | A subagent handoff is compact — the orchestrator reads a short result/summary, not the full raw output, unless the full output *is* the deliverable |
| D12 | If the skill's own output is quality-critical, creative, or easy to get subtly wrong, it defines a generate → review reflection loop against a checklist as concrete as this one |
| D13 | The reviewer role in any reflection loop is a **separate** subagent from the generator, reading only the artifact and the checklist — never the generator's reasoning |
| D14 | Every reflection loop states its pass bar explicitly (all-must-pass, or a numeric threshold) and a round cap — "loop until good" is not a stopping rule |
| D15 | Examples in the skill are concrete (real filenames, real values), not abstract placeholders like `<value>` |
| D16 | All file paths use forward slashes, even where the skill might run on Windows |
| D17 | Time-sensitive facts (current API versions, "as of" statements) sit in a section that's easy to find and update, not woven through the prose |
| D18 | A review step writes its findings to a **file** and returns only what routing needs — counts, failing item numbers, and the files those findings name — rather than returning the findings themselves for the orchestrator to relay |
| D19 | Fixes after a review are applied by subagents given the findings file's path and one file each, with any orchestrator-owned exception named explicitly (cross-file findings, or files no subagent owns) — the repair is delegated as deliberately as the review was |
| D20 | **Every** phase that produces a file dispatches a subagent to write it, leaving the orchestrating turn holding a reference to the artifact instead of the artifact — a path plus a line count, or a path plus a bounded summary. Score it by reading the step's own voice: "write `SKILL.md` to the target directory" fails; "launch a subagent to write `SKILL.md`, return its path and a five-line summary" passes. One delegated producing phase does not excuse a second one written inline. **One carve-out, and it is narrow — a manifest.** The orchestrator may write a file itself only when all three hold: **(a)** its content is decisions the orchestrating turn made, or handles it already holds, rather than material it must compose; **(b)** it is **one line per decision or artifact with no prose body** — no paragraph, no explanation, no sections; and **(c)** the skill states a number bounding how many such lines it carries, or has already stated one upstream that bounds them, and that number is below the 20-line authoring threshold in the boundary note below. `.cache/skill-architect/spec-<slug>.md` written as "at most 8 lines, one line per decision, each naming the choice and the path it implies" is the shape that passes. **A prose document does not become a manifest by acquiring a line cap**: "write the design spec, keep it under 40 lines" fails (a), (b) and (c) at once, and that defect is the reason this item exists. Anything that produces a body, delegate |
| D21 | Every subagent dispatch in the skill's instructions names what comes back **and caps it with a number** — a stated shape ("each file written with its line count", "counts plus failing item ids plus the files they name") plus a numeric bound: a line, item, or word count ("at most 12 lines", "no more than 5 findings", "under 50 words"). Qualitative hedges are not caps and score FAIL — "short", "brief", "concise", "a summary", "a clause or two" leave two reviewers free to read the same bound differently. A dispatch that trails off at "report back when done" fails even where the rest of the delegation is right |
| D22 | Every subagent dispatch names **three** things — where the input is, what to do, and where the output goes — and names the input and the output as **paths**, never as content. A path may be literal (`.cache/design-brief/docs-digest.md`) or a variable the skill has already bound (`MOCK_TARGET`, read from its state script); what it may not be is the file itself. A dispatch that pastes a template, a source document, a digest, a rubric or a prior artifact's body into the prompt text scores FAIL however convenient, because that body is then in the orchestrator's context — the exact cost the delegation was meant to avoid. Score it by looking inside the prompt block for file *contents*: quoted markup, an inlined checklist, a pasted draft. A path plus a clause saying what it holds passes; the thing itself does not. A dispatch that states no output destination also fails — a subagent told what to do but not where to put it returns the work as text. Where a step's input genuinely is not a file — a web lookup, a value the user just typed — the path requirement applies to the output only and the input side scores N/A, not FAIL. **Scope: the dispatch prompt.** D22 scores what the orchestrator's prompt carries; whether the work reached disk and the next agent was told where it is belongs to D10, and what comes *back* belongs to D11 and D21. Score a pasted body here and nowhere else — one mistake, one FAIL |

**The D20/N5 boundary is volume, not importance.** A phase is delegation-shaped when it writes a
body — roughly 20 lines or more — or reads more than a file or two, however easy the decision behind
it was; a 200-line file costs 200 lines of context whether it took five minutes or an hour to
decide. Below that bar (a frontmatter-only stub, a single value looked up) N5 governs and inline is
the correct call. Never rescue an inline draft under N5 on the grounds that it was simple.

**Authoring and editing are different cases, and the volume line applies only to authoring.** D20
covers bringing a body into existence, which pulls every line of it through the orchestrating turn.
An in-place edit of an artifact that **already exists** falls on the N5 side and is correctly done
inline whatever its size, because the orchestrator needs only the region being changed: a twenty-line
revision to a 400-line document costs twenty lines, not 400. So a refinement step that applies user
feedback as a small edit scores PASS on D20 inline, and a reviewer must not fail it for sitting near
the 20-line mark — that threshold gates new files, not revisions to old ones. An edit crosses back
into authoring by the rule below, and only by that rule.

**Where an edit crosses back into authoring: count lines held, not sections touched.** Let `L` be
the number of lines the orchestrating turn must read or write to make the change correctly — the
lines changed, plus any surrounding lines it has to read to place them. Let `N` be the file's
current line count. The change is **authoring, and D20 applies**, when `L > N/2` **or** `L > 100`;
otherwise it is an **edit, and N5 governs** — inline is correct. Both halves do work: the ratio
catches the rewrite of a short file, and the flat 100 catches the case where half of a long file is
still body-sized, because past roughly five times D20's 20-line authoring floor "you only pay for
the region" stops being true — the region *is* a body. Sections are not the unit and never decide
it: four of six regions touched is an edit when those regions are 40 lines of a 600-line document,
and authoring when they are 400. Where a skill's step is written generically and no size is
knowable, score the case its own wording describes — "change only the regions the user named" is
bounded by construction and passes; "rebuild the page from the new direction" is authoring under a
different name. Reviewers: ask whether the file already exists, then compute `L` against `N`. Do not
fall back to "feels like a rewrite."

**Dispatch length is a signal, not a scored item.** The ideal dispatch approaches "your turn",
because the subagent's own skill or reference file already encodes where its input lives and where
its output goes; a dispatch that has grown long with input/output plumbing usually signals knowledge
that belongs one layer down, in the file the subagent reads anyway. Reviewers may raise that as a
note, but it never produces a FAIL and no item scores it: no threshold separates a dispatch that is
long because the task is genuinely intricate from one that is long because it restates a reference
file, and an all-must-pass rubric cannot carry an item two reviewers would split on. D22 already
catches the version of this that *is* checkable — plumbing that arrives as pasted content rather
than as a path.

## DON'T

| # | Item |
|---|---|
| N1 | Description written in first or second person ("I can help you...", "You can use this to...") |
| N2 | SKILL.md re-explains things Claude already knows (what a PDF is, what JSON is, how git works) — every paragraph should fail the test "would Claude get this wrong without it?" |
| N3 | A reference file exists that nothing in SKILL.md links to, or that's only reachable two hops deep |
| N4 | A script defers a foreseeable error back to Claude with a bare stack trace instead of handling it |
| N5 | A subagent is spawned for work that is trivial **by volume** — a handful of lines written or read, such as a one-line edit or a frontmatter-only stub — and would've been just as cheap inline; delegation that doesn't protect context is overhead wearing a costume. Judged on lines produced or consumed, not on how simple the decision was (see the D20/N5 boundary above) |
| N6 | A reflection loop's reviewer is the same subagent (or same context) as the generator — that's the artifact grading its own homework |
| N7 | A reflection loop runs with no iteration cap, or the cap is high enough to be a cost problem in practice |
| N8 | A reviewer manufactures findings to look thorough when the artifact is actually fine — "PASS" must be a real, expected verdict by the second round, not a rare event |
| N9 | The skill offers several equally-weighted tool/library options ("use pdfplumber, or PyPDF, or...") instead of one clear default with a named escape hatch |
| N10 | Generated/output files a user might hand-edit are indistinguishable from files the skill will silently overwrite next run |
| N11 | The orchestrating context reads a full review report, or hand-edits the artifact the review just scored — a skill that delegates the writing and the reviewing but takes the repairing back has spent its saving at the last step |
| N12 | The main flow drafts an artifact inline and *then* spawns a subagent to review it — the checking delegated, the producing kept. Includes the partial form: one artifact written in the orchestrating turn while the next is handed off. The inline draft then sits in context through every review and fix round, so the expensive half was never delegated at all |

## Sanity check before relying on this checklist

Before trusting a reflection loop built on this file, ask: **could this checklist actually fail a
bad draft?** Take the artifact and mentally construct the worst plausible first draft — a
500-line wall of instructions with no reference files, a script that swallows exceptions, a
"reviewer" that's really the same subagent re-reading its own output. Walk it against DO/DON'T
above. If every item would still score PASS, the checklist isn't discriminating and the reflection
loop is theater. Tighten the specific item that let it through before running the loop for real.

**The thin-orchestrator test (D20, D21, D22, N12).** These four fail a specific bad draft, so check
them against it directly. Take a SKILL.md whose flow reads *"write the design doc to
`docs/design.md`, then launch a reviewer subagent to check it"*, with that dispatch ending at "report
back when done." That draft must score **FAIL on D20** (the producing step is in the orchestrator's
own voice), **FAIL on D21** (the dispatch names no return shape and no cap), **FAIL on D22** (the
dispatch names no input path and no destination for the review's output, so the findings can only
come back as text) and **FAIL on N12** (the review is delegated, the production isn't) — and N5 must
not rescue it, since a design doc is not trivial by volume. Then take the corrected draft: a
generator subagent is given its brief's path and writes `docs/design.md`, returning that path and a
line count; a separate reviewer subagent is given the doc's path and the checklist's path, writes
findings to `.cache/review-r1.md`, and returns counts plus failing item ids; each dispatch names its
inputs and its output destination as paths and caps its return at a stated number of lines. That one
must be able to score PASS on all four at once, with no item forcing a contradiction. If the bad
example survives any of the four, or the corrected one can't pass them all, the item is decorative
rather than gradable — rewrite it before the loop runs.
