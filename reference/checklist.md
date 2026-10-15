# Skill quality checklist

Apply the core checks to the relevant files and behavior. Conditional checks
apply only when the corresponding pattern exists; its absence is not a defect.
Use PASS / FAIL / N/A with specific evidence. A sound skill can pass without
references, subagents, reflection, a manifest, or an orchestrator.

## Core checks

| Check | Pass condition |
|---|---|
| Purpose and discovery | Name is plain and valid; description states behavior and concrete triggers in third person. Applicability is not repeated in the body. |
| Body structure | Outcome and goal, optional Instructions, and Definition of Done are clear; equivalent existing headings are acceptable for targeted improvements. |
| Outcome and requirements | The useful result and completion boundary are clear. Consequential constraints and bespoke preferences are explicit; output specifications exist only where needed. |
| Completion standard | Observable acceptance criteria and evidence establish success; a separate review workflow is not required. |
| Minimality | Each instruction, file, script, and stage solves a current problem or requirement. No speculative machinery. |
| Improvement scope | The change resolves the reported problem, preserves useful behavior, and considers removal, simplification, or replacement before addition. |
| Determinism | Every deterministic step executes a script rather than requiring repeated agent derivation. Existing suitable scripts may be reused. |
| Script usability | Run commands, inputs, outputs, dependencies, foreseeable errors, and non-obvious constants are handled clearly. |
| Disclosure | Growing detail is moved out of the common path when needed; references are directly linked and their reading conditions clear. |
| File hygiene | Links resolve, paths use forward slashes, obsolete files and links are removed, and long references have contents sections. |
| Method | The agent chooses the approach unless guidance is needed. Information gathering is part of method; known constraints and scripts are included upfront, further steps or detail address observed failures. |
| Authorization | The workflow respects established authorization and asks only about unresolved consequential choices. |
| Output ownership | Generated outputs and user-maintained files are distinguished; overwrite behavior is clear. |
| Validation | Structural checks and a proportionate representative check support the completion claim; limitations are stated. |

## Conditional workflow checks

| Pattern | Pass condition |
|---|---|
| Routing | Selection criteria choose the appropriate specialist without running unrelated workers. |
| Chaining | Dependent stages consume completed file outputs, with staged context justified by the task. |
| Parallel fan-out | Independent units have disjoint ownership; combined results are checked for omissions and duplication. |
| Vote/rank fan-out | Independent alternatives use different approaches and explicit ranking criteria; agreement is not treated as proof of correctness. |
| Independent stages | A concrete accuracy problem warrants generate → verify → fix. Each stage has a separate subagent, one pass each by default. |
| Verification | The verifier checks artifacts against requirements independently, cites actionable locations and evidence, and can return PASS without inventing defects. |
| Fixing | The fixer makes necessary repairs without unrelated redesign; applicable deterministic checks confirm the changes. |
| Reflection | Meaningful unresolved defects justify additional verify → fix rounds; acceptance criteria, a small round cap, and stopping rules are explicit. |
| Workers | Context load or distinct responsibilities justify a thin orchestrator and coherent worker tasks; file creation alone is not the reason. |
| Handoffs | Whenever subagents are used, dispatches name file input paths, task, output file destination, ownership, and a bounded return. Artifacts, research, and findings are written to files regardless of size; subsequent agents read them by path. Returns contain paths and compact status summaries, not relayed work. |
| Coordination | Worker edits have clear ownership, cross-file changes are coordinated, and large artifacts are not repeatedly copied just to relay them. |
| Simplification | Obsolete workflow patterns are removed or replaced when their original problem disappears. |

## Reviewing without expanding the skill

A FAIL names a current unmet requirement or an observed execution problem, the
location, and the smallest effective remedy. A suggestion that only anticipates
a hypothetical future need is not a FAIL. Score one defect once rather than
multiplying it across overlapping checks.

Before recommending new machinery, ask whether deleting or replacing an existing
rule would solve the problem. Before recommending more review, ask whether a
script can check the error exactly. Do not require a full audit for a targeted fix.

Sanity-check the rubric: an unscripted deterministic operation, broken reference,
or unbounded reflection loop must fail; a small, working single-agent skill must
be able to pass. If the checklist forces complexity without evidence, correct the
checklist rather than expanding the skill to appease it.
