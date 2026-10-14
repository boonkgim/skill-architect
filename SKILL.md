---
name: skill-architect
description: Creates a minimal working skill and improves existing skills with the smallest effective change. Scripts deterministic steps, discloses detail progressively as the skill grows, and introduces independent verification, reflection, or workers only when concrete accuracy or execution problems justify them. Use when the user asks to create a skill, turn a repeated procedure into a skill, write a SKILL.md, or improve a skill's structure.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch
---

# Skill Architect

Build the smallest skill that handles the current need. Evolve it from actual use:
add, remove, or replace structure according to concrete problems, not hypothetical
future needs. Balance agent autonomy with predictable quality, and limit context
load through progressive disclosure.

## Rules that always apply

- **Deterministic steps become scripts.** If the same input produces the same
  correct output, execute a script rather than asking the agent to derive it again.
  A simple script is sufficient; reuse an existing suitable script where possible.
- **Disclose detail progressively as the skill grows.** Keep the common workflow
  in `SKILL.md`; move substantial optional guidance to directly linked references.
  Do not create supporting files merely to satisfy a preferred directory structure.
- **Prefer the smallest effective improvement.** First consider removing,
  simplifying, or replacing existing instructions. Add instructions or workflow
  stages only when those options are insufficient. Preserve useful behavior.
- **Default to one agent.** Producing a file, creative work, and skill length alone
  do not require subagents, reflection, or an orchestrator.
- **When delegating, use files.** Subagents read file inputs by exact path and
  write artifacts, research, and review findings to named files. Return paths and
  a compact status summary; subsequent agents read the files, not relayed content.

Read [reference/authoring-guide.md](reference/authoring-guide.md) when a design
choice needs more detail. Use [reference/checklist.md](reference/checklist.md) for
a proportionate final check; advanced items are conditional, not prerequisites.

## Minimum useful content

Put applicability in the frontmatter description; do not repeat it in the body.
Cover these considerations without requiring a heading for each:

- **Outcome:** the useful result and completion boundary.
- **Requirements and preferences:** constraints and bespoke standards the agent
  cannot infer. Specify output format or structure only when it matters.
- **Completion standard:** observable acceptance criteria and how to establish
  success. A quality gate can be one sentence; it does not require a review stage.
- **Method, only as needed:** let the agent choose how. Information gathering is
  part of method; prescribe sources or questions only where needed. Include known
  constraints and deterministic scripts upfront; add high-level steps, then detail,
  only where failures show that further procedural guidance helps.

## Create

1. Identify one real use case: purpose, trigger, input, expected result, essential
   constraints, and target directory. Infer from the request and repository
   conventions; ask only for missing information that affects the result.
2. Check for an existing skill that can be reused or adapted. Research only domain
   facts needed for the current task that are missing or require verification.
3. Write the minimum useful `SKILL.md` and scripts for its deterministic steps.
   Use the content considerations above; keep the method open where possible.
4. Try the common path on a representative request, using a safe fixture or
   walkthrough if execution would cause unwanted external effects. Check the
   intended result and fix the actual failure; do not invent an evaluation harness.
5. Run the structural validator and applicable checklist items. Stop when the
   current need is met; leave speculative enhancements out.

## Improve

1. Start with the reported problem and intended behavior. Read the relevant
   instructions and dependencies, expanding only as needed to understand the fix.
   A full audit is appropriate only when requested or the problem spans the skill.
2. Identify the smallest intervention. Can deletion, clearer wording, replacement
   with a script, or removal of an obsolete stage solve it? Avoid layering a new
   exception over an instruction that should instead change.
3. Apply the authorized change directly. Do not introduce a second approval gate
   for work the user has already requested. Seek clarification only when a material
   choice remains unresolved.
4. Check the changed path and any affected behavior; run the structural validator.
   Remove obsolete references, scripts, or workflow stages as part of the change.
5. Report what changed, why, and what was checked. State any unresolved limitation.

## Add workflow patterns only when needed

These are independent choices, not an obligatory ladder:

| Pattern | Evidence that justifies it |
|---|---|
| Generate → verify → fix | Accuracy is insufficient and independent verification can address the observed errors. Run one pass of each stage with a separate subagent for each. |
| Reflection: repeat verify → fix | One pass leaves meaningful defects unresolved. Define concrete acceptance criteria and a small round cap before repeating. |
| Thin orchestrator + workers | A large skill's context load or distinct responsibilities demonstrably impair execution. Delegate the affected work and keep coordination small. |

A small skill may need independent verification without workers. A large skill
may need workers without reflection. Use scripts for deterministic checks in every
pattern. Reassess existing patterns during improvement: remove or replace them
when their original problem disappears, including when a script makes review
stages unnecessary. See the authoring guide for contracts and stopping rules.

## Validate and finish

Run the bundled, standard-library-only checker:

```bash
python3 <this-skill-dir>/scripts/validate_skill.py <target-skill-dir>
```

Fix relevant `FAIL`s before reporting completion. Address `WARN`s or explain why
one remains; do not turn a warning into an unrelated redesign. Structural checks
cannot establish behavioral accuracy, so report the representative check separately.
Keep the final summary proportional to the change: files changed, resulting
behavior, validation, and any unresolved issue. Do not commit or push unless asked.
