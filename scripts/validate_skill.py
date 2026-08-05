#!/usr/bin/env python3
"""Deterministic structural checks for a SKILL.md — run before any LLM review.

Checks frontmatter validity, body length, reference-file link depth and table of
contents, script constant hygiene, and path style. This does not judge whether the
skill is well-designed — that's what the checklist-driven reflection loop is for.
See ../reference/checklist.md for the items this script can't check mechanically.

Usage:
    python3 validate_skill.py <path-to-skill-dir-or-SKILL.md>

Exit code 0 if there are no FAILs (WARNs are printed but don't fail the run),
1 if there is at least one FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RESERVED_NAME_WORDS = ("anthropic", "claude")
MAX_NAME_LEN = 64  # frontmatter `name` limit per Claude Code skill-authoring docs
MAX_DESCRIPTION_LEN = 1024  # frontmatter `description` limit per the same docs
MAX_BODY_LINES = 500  # official guidance: split into reference files above this
REFERENCE_TOC_MIN_LINES = 100  # official guidance: reference files this long need a "## Contents"

MD_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")
WINDOWS_PATH_RE = re.compile(r"\b\w+\\(scripts|reference|templates)\\")
FIRST_PERSON_RE = re.compile(r"^\s*(I |I'm |I can\b|You can\b|You should\b|We )")
TRIGGER_CLAUSE_RE = re.compile(r"\buse when\b|\buse for\b|\buse to\b|\bwhen the user\b", re.IGNORECASE)
CONSTANT_ASSIGN_RE = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*-?\d+(\.\d+)?\s*(#.*)?$")


def find_skill_md(target: Path) -> Path:
    if target.is_file():
        return target
    candidate = target / "SKILL.md"
    if candidate.exists():
        return candidate
    raise SystemExit(f"No SKILL.md found at {target}")


def split_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    """Parse the flat key: value YAML frontmatter SKILL.md files use.

    Not a general YAML parser — SKILL.md frontmatter is flat scalars, so a
    real YAML library would be a dependency this stdlib-only script doesn't need.
    """
    errors: list[str] = []
    if not text.startswith("---\n"):
        errors.append("File does not start with '---' frontmatter delimiter")
        return {}, text, errors
    end = text.find("\n---", 4)
    if end == -1:
        errors.append("Frontmatter is not closed with a second '---'")
        return {}, text, errors
    raw_fm = text[4:end]
    body = text[end + 4:].lstrip("\n")

    fields: dict[str, str] = {}
    key: str | None = None
    for line in raw_fm.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) and key:
            fields[key] += " " + line.strip()
            continue
        if ":" not in line:
            errors.append(f"Unparseable frontmatter line: {line!r}")
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        fields[key] = value.strip()
    return fields, body, errors


def check_name(name: str) -> list[str]:
    if not name:
        return ["FAIL name: missing"]
    issues = []
    if len(name) > MAX_NAME_LEN:
        issues.append(f"FAIL name: {len(name)} chars > {MAX_NAME_LEN} limit")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        issues.append(f"FAIL name: {name!r} must be lowercase letters/numbers/hyphens only")
    lowered = name.lower()
    for word in RESERVED_NAME_WORDS:
        if word in lowered:
            issues.append(f"FAIL name: contains reserved word {word!r}")
    if "<" in name or ">" in name:
        issues.append("FAIL name: contains XML-like tag characters")
    return issues


def check_description(desc: str) -> list[str]:
    if not desc:
        return ["FAIL description: missing"]
    issues = []
    if len(desc) > MAX_DESCRIPTION_LEN:
        issues.append(f"FAIL description: {len(desc)} chars > {MAX_DESCRIPTION_LEN} limit")
    if FIRST_PERSON_RE.match(desc):
        issues.append(
            "FAIL description: written in first/second person — must be third person "
            '("Processes X" not "I can help with X")'
        )
    if not TRIGGER_CLAUSE_RE.search(desc):
        issues.append(
            "WARN description: no clear 'use when...' trigger clause found — "
            "Claude may not know when to select this skill"
        )
    return issues


def check_body(body: str, skill_dir: Path) -> list[str]:
    issues: list[str] = []
    lines = body.splitlines()
    if len(lines) > MAX_BODY_LINES:
        issues.append(
            f"WARN body: {len(lines)} lines > {MAX_BODY_LINES} — split content into reference files"
        )

    for i, line in enumerate(lines, 1):
        if WINDOWS_PATH_RE.search(line):
            issues.append(f"WARN body:{i}: possible Windows-style backslash path — use forward slashes")

    direct_links = set(MD_LINK_RE.findall(body))
    for link in sorted(direct_links):
        ref_path = (skill_dir / link).resolve()
        if not ref_path.exists():
            issues.append(f"FAIL body: linked reference file does not exist: {link}")
            continue
        ref_text = ref_path.read_text(encoding="utf-8", errors="replace")
        nested_links = set(MD_LINK_RE.findall(ref_text))
        deeper = nested_links - direct_links
        if deeper:
            issues.append(
                f"WARN body: {link} links to {sorted(deeper)}, which SKILL.md does not link "
                "directly — keep references one level deep from SKILL.md"
            )
        ref_lines = ref_text.splitlines()
        if len(ref_lines) > REFERENCE_TOC_MIN_LINES and not re.search(
            r"^#{1,2}\s*Contents\b", ref_text, re.MULTILINE | re.IGNORECASE
        ):
            issues.append(
                f"WARN body: {link} is {len(ref_lines)} lines with no '## Contents' heading near the top"
            )
    return issues


def check_scripts(skill_dir: Path) -> list[str]:
    issues: list[str] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for script in sorted(scripts_dir.rglob("*.py")):
        text = script.read_text(encoding="utf-8", errors="replace")
        script_lines = text.splitlines()
        for i, line in enumerate(script_lines, 1):
            m = CONSTANT_ASSIGN_RE.match(line.strip())
            if not m:
                continue
            has_inline_comment = "#" in line.split("=", 1)[1]
            prev_line = script_lines[i - 2].strip() if i >= 2 else ""
            has_comment_above = prev_line.startswith("#")
            if not has_inline_comment and not has_comment_above:
                issues.append(
                    f"WARN {script.relative_to(skill_dir)}:{i}: constant {m.group(1)} has "
                    "no justifying comment — avoid voodoo constants"
                )
    return issues


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    skill_md = find_skill_md(Path(sys.argv[1]))
    skill_dir = skill_md.parent
    text = skill_md.read_text(encoding="utf-8")
    fields, body, fm_errors = split_frontmatter(text)

    issues: list[str] = [f"FAIL frontmatter: {e}" for e in fm_errors]
    issues += check_name(fields.get("name", ""))
    issues += check_description(fields.get("description", ""))
    issues += check_body(body, skill_dir)
    issues += check_scripts(skill_dir)

    fails = [i for i in issues if i.startswith("FAIL")]
    warns = [i for i in issues if i.startswith("WARN")]

    print(f"Validating {skill_md}\n")
    if not issues:
        print("PASS — no structural issues found.")
        return 0

    for issue in fails + warns:
        print(issue)
    print(f"\n{len(fails)} FAIL, {len(warns)} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
