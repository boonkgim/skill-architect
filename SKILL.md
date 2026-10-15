---
name: skill-architect
description: Creates a minimal working skill and improves existing skills with the smallest effective change. Scripts deterministic steps, discloses detail progressively as the skill grows, and introduces independent verification, reflection, or workers only when concrete accuracy or execution problems justify them. Use when the user asks to create a skill, turn a repeated procedure into a skill, write a SKILL.md, or improve a skill's structure.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, AskUserQuestion, WebSearch, WebFetch
---

# Skill Architect

## Outcome and goal

Build the smallest skill that handles the current need. Balance agent autonomy
with predictable quality, and limit context load through progressive disclosure.
When improving, prefer removing, simplifying, or replacing existing instructions
before adding complexity. Preserve useful behavior.

Use this structure for authored skills:

- **Frontmatter:** what the skill does and when to use it. Keep applicability here.
- **Outcome and goal:** objective, consequential constraints and bespoke preferences,
  with output format or structure only when needed.
- **Instructions (optional):** methods the agent needs help with, including
  information gathering, scripts, and workflow patterns. Let it infer the rest.
- **Definition of Done:** observable acceptance criteria and evidence of success.
  Use a do/don't checklist where useful; one condition may be sufficient.

For targeted improvements, adapt existing headings rather than reorganizing the
whole skill just to match this structure.

## Instructions

### Rules that always apply

- **Deterministic steps become scripts.** Execute rather than re-derive mechanical
  work. Keep scripts simple and reuse existing suitable ones.
- **Use progressive disclosure as the skill grows.** Keep the common path in
  `SKILL.md`; directly link optional details and say when to read them. Remove
  redundant guidance before splitting files.
- **Preserve autonomy.** Include known constraints, fragile operations, and scripts
  upfront. Otherwise add high-level steps when observed failures warrant them,
  then details only if those steps are insufficient.
- **Default to one agent.** Add workflow patterns only for a concrete need.
- **When delegating, use files.** Give subagents exact file input paths and output
  destinations. They write artifacts, research, and findings to files and return
  paths plus compact status summaries. Subsequent agents read those files directly.

Read [reference/authoring-guide.md](reference/authoring-guide.md) for design details
or workflow contracts when needed. Use [reference/checklist.md](reference/checklist.md)
for a proportionate final check; conditional patterns are not prerequisites.

### Create

1. Identify a real use case, intended outcome, essential requirements, and target
   directory. Infer from the request and repository; ask only for consequential gaps.
2. Check for a reusable skill. Research only missing domain facts needed now.
3. Write the minimum useful skill using the structure above, plus scripts for
   deterministic steps. Leave procedural guidance out where the agent can infer it.
4. Try a representative request, using a safe fixture or walkthrough when needed.
   Fix actual failures; do not invent an evaluation harness.
5. Run structural validation and applicable completion checks. Stop when done.

### Improve

1. Start at the reported problem and read only the relevant instructions and
   dependencies. Perform a full audit only when requested or genuinely needed.
2. Choose the smallest effective intervention: remove, simplify, replace, or add.
   Avoid layering exceptions over a rule that should change.
3. Apply authorized changes directly. Ask only about unresolved consequential choices.
4. Check affected behavior and structure; remove obsolete files, links, or stages.
5. Report the result, checks, and any unresolved limitation.

### Workflow patterns, only as needed

Choose by the problem being solved; patterns may combine but are not a ladder.

| Pattern | When and how |
|---|---|
| Route | Select the appropriate specialised subagent based on the request. |
| Chaining | Use separate subagents for dependent stages when the work needs staged context or exceeds one agent's context capacity. |
| Generate → verify → fix | Accuracy needs improvement: run one pass of each stage with a separate subagent for each. |
| Reflection | One pass leaves meaningful defects: repeat verify → fix against explicit criteria, with a round cap and a stop rule for stalled progress. |
| Fan-out, parallel | Split independent high-volume work across subagents for throughput, then combine results. |
| Fan-out, vote/rank | Generate independent alternatives with different approaches, then select against explicit criteria; agreement alone does not prove correctness. |
| Thin orchestrator + specialised workers | Keep context light when scale or distinct responsibilities impair execution: the main agent delegates and coordinates; workers do the substantive work. |

Use scripts for deterministic checks in every pattern. Remove or replace patterns
when their motivating problem disappears. File-based handoffs apply to all of them.

## Definition of Done

- The skill meets the current outcome and consequential requirements, with a clear
  completion standard; a separate review workflow is conditional.
- A proportionate representative check supports the completion claim. Report
  limitations; structural validation alone does not prove behavioral accuracy.
- Run `python3 <this-skill-dir>/scripts/validate_skill.py <target-skill-dir>`.
  Fix relevant FAILs and address WARNs or explain them without unrelated redesign.
- No speculative workflow machinery or obsolete references remain. Keep the final
  report proportional: changed behavior, files, checks, and unresolved issues.
- Commit and push only when requested.
