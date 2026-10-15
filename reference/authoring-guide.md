# Authoring guide

## Contents

- Minimal creation and improvement
- Progressive disclosure
- Deterministic scripts
- Specificity and defaults
- Conditional workflow patterns
- File handoffs when delegating
- Frontmatter and discovery
- Proportionate validation

## Minimal creation and improvement

Start with one concrete request the skill should handle. Write only the guidance
needed to produce its expected result, plus scripts for deterministic operations.
Do not add an architecture spec, mapping report, manifest, or supporting reference
unless the current work actually needs it.

For an existing skill, start at the reported failure, not a comprehensive audit.
Preserve successful behavior while looking first for something to remove,
simplify, or replace. A tangled rule may need rewriting rather than another
exception. A review stage may be replaceable by an exact checker. Supporting files
may become unnecessary after simplification; remove them and update their links.

Ask only for consequential information that cannot be inferred. Follow the user's
established scope and authorization rather than inserting a generic approval gate.
If a request covers unrelated workflows, discuss their separation only when one
skill cannot express clear triggers and execution paths; splitting is not a goal
in itself.

## Progressive disclosure

Use one `SKILL.md` while it remains clear. As it grows, keep essential rules and
the common execution path in the body and link to optional details at the point
where they become relevant. Explain when each reference should be read.

Useful shapes are a common path with deeper references, separate references for
independent domains, or a short default with a linked exceptional branch. Choose
by the actual reading need, not by a mandatory template.

Link every reference directly from `SKILL.md`, use forward-slash relative paths,
and keep links valid when content moves. Keep the body below 500 lines; add a
contents section to references longer than 100 lines. These are readability
limits, not reasons to pad a small skill or thresholds for spawning workers.
Cut redundant instructions before splitting them into more files.

## Deterministic scripts

**Every deterministic step becomes a script.** Parsing, calculations, schema
validation, convention checks, and fixed file generation should not be re-derived
from prose each run. Keep the script as simple as the operation permits; existing
scripts can be reused rather than duplicated.

- State exactly how to run it, required inputs, and expected outputs or exit codes.
- Declare dependencies; prefer no extra dependency when a simple solution suffices.
- Handle foreseeable errors with specific messages or justified fallbacks. Do not
  silently swallow failures or leave routine failures as an unexplained stack trace.
- Explain non-obvious constants with comments and expose genuinely variable inputs
  as arguments rather than adding speculative configuration.
- Use a template plus a render/copy script for fixed file bodies with variable
  fields, rather than asking the agent to retype a canonical code block.
- Distinguish generated outputs from user-maintained files and prevent accidental
  overwrites. Do not turn a small helper into a framework.

## Specificity and defaults

Use Outcome and goal, optional Instructions, and Definition of Done as the basic
body structure. Keep constraints and preferences with the outcome, and methods
under Instructions. Adapt existing headings for targeted changes rather than
forcing a full restructure. Define acceptance criteria before prescribing a method.
Specify output structure only when it affects use or compatibility; a resulting
state can be the outcome.
Separate mandatory requirements from adaptable preferences. Avoid background
explanations an agent already knows.

Let the agent infer the method, including how to gather information. Name sources,
questions, tools, or sequences only when the task needs that guidance. Include
known fragile operations and constraints upfront rather than waiting for failure;
deterministic operations always use scripts. Otherwise add high-level steps when
observed failures warrant them, then details only if those steps are insufficient.

Every skill needs a completion standard, even when the agent knows what good work
looks like. State what evidence establishes success; avoid vague gates such as
"ensure quality." This does not require a separate checklist, reviewer, or loop.

## Conditional workflow patterns

Begin with a single agent executing and checking the skill. Add only the pattern
that addresses a concrete problem; do not automatically combine these patterns.

**Route:** choose the specialised subagent whose responsibility fits the request.
Use clear selection criteria and a fallback for ambiguous cases. Do not run every
specialist when only one applies.

**Chaining:** delegate dependent stages when intermediate results feed the next
stage and staged context is useful. Each stage writes its output before the next
reads it. Keep only coordination state in the parent, especially when the whole
task would exceed one context window.

**Generate → verify → fix:** when accuracy is insufficient and independent
judgment can catch the observed errors, use separate subagents for the generator,
verifier, and fixer. Run one pass of each. Give the verifier the artifact and
requirements, without the generator's rationale biasing its judgment. It reports
specific defects, with locations and evidence, rather than speculative improvements.
The fixer changes only what is needed; deterministic checks confirm those changes.
Do not silently repeat the cycle or claim a clean independent re-review occurred.

**Reflection:** only if that pass leaves meaningful defects unresolved, repeat
verify → fix. Before starting, name concrete acceptance criteria and a small cap
on additional rounds (normally at most two). Stop when those criteria are met,
the cap is reached, or a finding persists without progress. Report unresolved
issues instead of hiding them or looping indefinitely. A verifier must be able to
return a clean pass; preferences and hypothetical enhancements are not defects.

**Fan-out, parallel:** split independent high-volume work into homogeneous units
and run them concurrently when capacity permits. Assign disjoint output ownership,
then combine results and check for missing or duplicate units. Do not parallelize
steps that depend on unfinished results.

**Fan-out, vote/rank:** have subagents solve the same task independently using
different approaches, then compare their outputs against explicit acceptance and
ranking criteria. Preserve alternatives in separate files. Agreement is a signal,
not proof; verify factual or mechanical claims against evidence or scripts.

**Thin orchestrator + specialised workers:** only when a large skill's context
load or distinct responsibilities impair execution, separate coordination from
the affected work.
The orchestrator holds decisions and routes work; workers read, produce, verify,
or repair the material they own. Give workers coherent tasks, not a mandatory
one-worker-per-file fan-out. Cross-file changes should have one clear owner.
The main agent delegates and coordinates rather than performing the workers'
substantive work. Avoid rereading large artifacts merely to relay them; read only
what a coordinating decision actually needs.

Independent verification can be useful without a thin orchestrator; workers can
be useful without reflection. During improvement, simplify or remove patterns
whose motivating problem is now solved. If needed tools are unavailable, state the
limitation and perform available checks without claiming independence.

## File handoffs when delegating

Once subagents are used, file-based handoff is mandatory regardless of output size.
Give agents exact paths to file inputs; they write artifacts, research results,
and review findings to named files. Subsequent agents read those files directly
rather than receiving their contents relayed through the coordinator. Reuse
existing artifacts as inputs; no separate manifest or spec is required.

Each dispatch states inputs, task, output destination, ownership, and what to
return. File inputs are paths, never pasted bodies; directly supplied values need
no wrapper file. Returns contain paths and compact status summaries, not the work
itself. Bound returns to what coordination needs, for example the output path and
up to five status items. Use descriptive cache paths such as
`.cache/<skill-name>/review-r1.md` for intermediate reports. Keep worker tools
scoped to the task, and avoid overlapping edits.

## Frontmatter and discovery

Use a plain activity name: lowercase letters, numbers, and hyphens, no more than
64 characters; avoid reserved platform words such as `anthropic` and `claude`.
Write a third-person description of what the skill does and when to use it, with
concrete user trigger terms. Keep applicability here rather than repeating it in
the body. Keep it under 1024 characters. Preserve repository
conventions and only declare tool restrictions the skill actually needs.

## Proportionate validation

Run `scripts/validate_skill.py` for structural checks. Use the checklist on the
changed behavior and applicable architecture; mark conditional items N/A when the
pattern is absent. Verify a representative use case where practical, using safe
fixtures or a walkthrough when needed. A targeted improvement needs a targeted
check, not a new evaluation system or mandatory multi-agent review.
