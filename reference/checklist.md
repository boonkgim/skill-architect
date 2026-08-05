# Skill quality gate — the shared checklist

## Contents
- How this file is used
- DO
- DON'T
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
| D10 | Work handed from one subagent to another goes through a file on disk, and the receiving side is told the exact path to read — not pasted back through the conversation |
| D11 | A subagent handoff is compact — the orchestrator reads a short result/summary, not the full raw output, unless the full output *is* the deliverable |
| D12 | If the skill's own output is quality-critical, creative, or easy to get subtly wrong, it defines a generate → review reflection loop against a checklist as concrete as this one |
| D13 | The reviewer role in any reflection loop is a **separate** subagent from the generator, reading only the artifact and the checklist — never the generator's reasoning |
| D14 | Every reflection loop states its pass bar explicitly (all-must-pass, or a numeric threshold) and a round cap — "loop until good" is not a stopping rule |
| D15 | Examples in the skill are concrete (real filenames, real values), not abstract placeholders like `<value>` |
| D16 | All file paths use forward slashes, even where the skill might run on Windows |
| D17 | Time-sensitive facts (current API versions, "as of" statements) sit in a section that's easy to find and update, not woven through the prose |

## DON'T

| # | Item |
|---|---|
| N1 | Description written in first or second person ("I can help you...", "You can use this to...") |
| N2 | SKILL.md re-explains things Claude already knows (what a PDF is, what JSON is, how git works) — every paragraph should fail the test "would Claude get this wrong without it?" |
| N3 | A reference file exists that nothing in SKILL.md links to, or that's only reachable two hops deep |
| N4 | A script defers a foreseeable error back to Claude with a bare stack trace instead of handling it |
| N5 | A subagent is spawned for trivial, single-shot work that would've been just as cheap inline — delegation that doesn't protect context is overhead wearing a costume |
| N6 | A reflection loop's reviewer is the same subagent (or same context) as the generator — that's the artifact grading its own homework |
| N7 | A reflection loop runs with no iteration cap, or the cap is high enough to be a cost problem in practice |
| N8 | A reviewer manufactures findings to look thorough when the artifact is actually fine — "PASS" must be a real, expected verdict by the second round, not a rare event |
| N9 | The skill offers several equally-weighted tool/library options ("use pdfplumber, or PyPDF, or...") instead of one clear default with a named escape hatch |
| N10 | Generated/output files a user might hand-edit are indistinguishable from files the skill will silently overwrite next run |

## Sanity check before relying on this checklist

Before trusting a reflection loop built on this file, ask: **could this checklist actually fail a
bad draft?** Take the artifact and mentally construct the worst plausible first draft — a
500-line wall of instructions with no reference files, a script that swallows exceptions, a
"reviewer" that's really the same subagent re-reading its own output. Walk it against DO/DON'T
above. If every item would still score PASS, the checklist isn't discriminating and the reflection
loop is theater. Tighten the specific item that let it through before running the loop for real.
