#!/usr/bin/env python3
"""Vendored Guild DF-1 guard.

Upstream: EngineeringGuild/Engineering-Guild
Upstream commit: a88fad3966b5c416a113d929b214e6c1a0c6c59d
Upstream path: tools/docs-lint/docs_lint.py
Vendored: 2026-08-12

Temporary local copy because this repository's GitHub Actions identity cannot
currently resolve the private cross-repository hub action. Track the supply-chain
fix in Engineering-Guild issue #70. Replace this copy through a reviewed PR when
central immutable distribution becomes available; do not edit it ad hoc.
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

FRONTMATTER_REQUIRED = ("doc", "version", "standard", "status", "updated")
DOSSIER_PATTERN = re.compile(r"(^|/)docs/\d\d_[^/]+\.md$")
DECISIONS_PATTERN = re.compile(r"DECISIONS[^/]*\.md$", re.I)
DEC_ID = re.compile(r"^\|\s*(DEC-[A-Z0-9]*-?\d+)\s*\|")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
SKIP_DIRS = {".git", "node_modules", "_archive", ".obsidian", "dist", "build"}

AGENT_SKILL_PATTERN = re.compile(r"(^|/)skills/.+/SKILL\.md$")
AGENT_SKILL_TEMPLATE_PATTERN = re.compile(r"(^|/)templates/SKILL_TEMPLATE\.md$")

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub PAT"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{22,}"), "GitHub fine-grained PAT"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}"), "OpenAI key"),
    (re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"), "Anthropic key"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"eyJhbGciOiJ[A-Za-z0-9_-]{40,}\.[A-Za-z0-9_-]{40,}\.[A-Za-z0-9_-]{20,}"), "signed JWT"),
]

BRANCH_GRAMMAR = re.compile(
    r"^((caioascastilho|caioasc|claude|hermes[a-z0-9]*)/[a-z0-9][a-z0-9._-]+"
    r"|arm/MSN-\d+-[A-Z][A-Z0-9]*)$"
)
TITLE_GVS = re.compile(r"^(feat|fix|chore|docs|refactor|test|ci)\([a-z0-9-]+\): .+ \(v\d+\.\d+\.\d+(\.\d+)?\)$")
REFS_BLOCK = re.compile(r"^\s*Refs?:\s*((ENG-\d+|MSN-\d+|DEC-[\w-]*\d+|SPONSOR:\d{4}-\d{2}-\d{2})(\s*[|,·]\s*)?)+", re.M)

errors: list[str] = []


def err(path, msg, line=1):
    errors.append(f"{path}:{line}: {msg}")
    print(f"::error file={path},line={line}::{msg}")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = {}
    for ln in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", ln.strip())
        if m:
            fm[m.group(1)] = m.group(2)
    return fm


def is_agent_skill_artifact(path):
    normalized = str(path).replace("\\", "/")
    return bool(
        AGENT_SKILL_PATTERN.search(normalized)
        or AGENT_SKILL_TEMPLATE_PATTERN.search(normalized)
    )


def check_frontmatter(root, path, text):
    if is_agent_skill_artifact(path):
        return

    fm = parse_frontmatter(text)
    is_dossier = bool(DOSSIER_PATTERN.search(str(path)))
    if fm is None:
        if is_dossier:
            err(path, "dossier doc (docs/NN_*.md) missing YAML frontmatter (GUILD-DOC-STANDARD)")
        return
    missing = [k for k in FRONTMATTER_REQUIRED if not fm.get(k)]
    if missing:
        err(path, f"frontmatter missing required field(s): {', '.join(missing)}")
    std = fm.get("standard", "")
    if std and not re.match(r"^GUILD-DOC-STANDARD@\d+\.\d+\.\d+$", std):
        err(path, f"frontmatter 'standard' malformed: {std!r}")


def check_links(root, path, text):
    for m in MD_LINK.finditer(text):
        target = m.group(1)
        if re.match(r"^[a-z]+://|^mailto:|^@", target) or target.startswith("<"):
            continue
        resolved = (root / path).parent / target
        if not resolved.exists():
            line = text[: m.start()].count("\n") + 1
            err(path, f"relative link does not resolve: {target}", line)


def check_decisions_file(root, path, text, base):
    ids = [m.group(1) for ln in text.splitlines() if (m := DEC_ID.match(ln.strip()))]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        err(path, f"duplicate decision id(s) — the DEC-001-029/039 collision class: {', '.join(dupes)}")
    if base:
        diff = subprocess.run(
            ["git", "diff", "-U0", f"{base}...HEAD", "--", str(path)],
            capture_output=True, text=True, cwd=root).stdout
        removed = [ln[1:].strip() for ln in diff.splitlines()
                   if ln.startswith("-") and not ln.startswith("---") and DEC_ID.match(ln[1:].strip())]
        if removed:
            err(path, f"decision log is append-only — removed/edited DEC row(s): {removed[0][:80]}…")


def check_secrets(root, path, text):
    for pat, name in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            line = text[: m.start()].count("\n") + 1
            err(path, f"possible {name} committed (secret sweep)", line)


def changed_files(root, base):
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"],
                         capture_output=True, text=True, cwd=root).stdout
    return [Path(p) for p in out.splitlines() if p.strip()]


def all_files(root):
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            files.append(p.relative_to(root))
    return files


def run_lint(root, base, scope_all):
    files = all_files(root) if scope_all or not base else changed_files(root, base)
    for rel in files:
        fp = root / rel
        if not fp.exists() or fp.is_dir():
            continue
        try:
            text = fp.read_text(errors="ignore")
        except OSError:
            continue
        if fp.suffix in {".md", ".yaml", ".yml", ".json", ".py", ".toml", ".txt", ".env"}:
            check_secrets(root, rel, text)
        if fp.suffix == ".md":
            check_frontmatter(root, rel, text)
            check_links(root, rel, text)
            if DECISIONS_PATTERN.search(fp.name):
                check_decisions_file(root, rel, text, base)
    return errors


def run_pr_meta():
    branch = os.environ.get("PR_HEAD_REF", "")
    title = os.environ.get("PR_TITLE", "")
    body = os.environ.get("PR_BODY", "")
    if branch and not BRANCH_GRAMMAR.match(branch):
        err("PR", f"branch name violates §3 grammar: {branch!r}")
    if title and not TITLE_GVS.match(title):
        err("PR", f"PR title violates §3 grammar (type(scope): description (vX.Y.Z.B)): {title!r}")
    if body and not REFS_BLOCK.search(body):
        err("PR", "PR body missing the §2 'Refs:' block (ENG-XXX | MSN-XXX | DEC-* | SPONSOR:YYYY-MM-DD)")
    return errors


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    lint = sub.add_parser("lint")
    lint.add_argument("--root", default=".")
    lint.add_argument("--base", default=os.environ.get("PR_BASE_REF", ""))
    lint.add_argument("--all", action="store_true", help="full-repo audit instead of changed files")
    sub.add_parser("pr-meta")
    args = ap.parse_args()

    if args.cmd == "pr-meta":
        run_pr_meta()
    else:
        base = f"origin/{args.base}" if args.base and not args.base.startswith("origin/") else args.base
        run_lint(Path(args.root).resolve(), base or None, getattr(args, "all", False))

    if errors:
        print(f"\nguild-docs-lint: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("guild-docs-lint: clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
