#!/usr/bin/env python3
"""Validate repository markdown documentation hygiene.

This check must not require documentation files that do not exist in the
repository. It validates real markdown files and can optionally enforce metadata
headers for files that opt into the managed-doc convention.
"""

from __future__ import annotations

import argparse
from pathlib import Path

MANAGED_DOC_MARKER = "Managed document: true"
REQUIRED_MANAGED_FIELDS = ["Owner:", "Audience:", "Last reviewed:", "Status:"]

STALE_PHRASES = [
    "P0 implementation hardening started",
    "Partial / not complete",
    "still need durable persistence",
    "P1.1 must implement",
    "P1.2 must implement",
]


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        yield path


def validate_managed_headers(root: Path) -> list[str]:
    """Validate metadata only for docs that explicitly opt in."""
    errors: list[str] = []
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if MANAGED_DOC_MARKER not in text[:1000]:
            continue
        for field in REQUIRED_MANAGED_FIELDS:
            if field not in text[:1000]:
                errors.append(f"{path.relative_to(root)} missing managed-doc header field: {field}")
    return errors


def find_stale_phrases(root: Path) -> list[str]:
    warnings: list[str] = []
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in STALE_PHRASES:
            if phrase in text:
                warnings.append(f"{path.relative_to(root)} contains stale phrase: {phrase}")
    return warnings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--fail-on-stale", action="store_true")
    args = parser.parse_args()

    if not args.root.exists():
        raise SystemExit(f"Root path does not exist: {args.root}")

    errors = validate_managed_headers(args.root)
    warnings = find_stale_phrases(args.root)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors or (args.fail_on_stale and warnings):
        raise SystemExit(1)

    print("Documentation validation completed.")


if __name__ == "__main__":
    main()
