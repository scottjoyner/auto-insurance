#!/usr/bin/env python3
"""Validate repository markdown documentation hygiene.

This script intentionally starts as a lightweight policy check. It prevents new
operational docs from missing ownership/review metadata and warns on phrases
that often indicate stale implementation status.
"""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_HEADER_FILES = {
    "docs/00_documentation_index.md",
    "docs/07_employee_operating_manual.md",
    "docs/08_claims_crm_operating_guide.md",
    "docs/09_blockchain_security_review.md",
    "docs/10_markdown_cleanup_register.md",
}

STALE_PHRASES = [
    "P0 implementation hardening started",
    "Partial / not complete",
    "still need durable persistence",
    "P1.1 must implement",
    "P1.2 must implement",
]


def validate_required_headers(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_HEADER_FILES:
        path = root / rel_path
        if not path.exists():
            errors.append(f"Missing required doc: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for field in ["Owner:", "Audience:", "Last reviewed:", "Status:"]:
            if field not in text[:500]:
                errors.append(f"{rel_path} missing required header field: {field}")
    return errors


def find_stale_phrases(root: Path) -> list[str]:
    warnings: list[str] = []
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
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

    errors = validate_required_headers(args.root)
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
