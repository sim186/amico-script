#!/usr/bin/env python3
"""Simple semantic version bumping and changelog helper.

Usage:
  python scripts/bump_version.py [major|minor|patch] "Changelog entry text"

This will:
- read the current version from `VERSION`
- bump the requested component
- write the new version back to `VERSION`
- move the top `Unreleased` items into a new changelog section for the new version
- optionally append a provided changelog entry under the new version
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"


def read_version() -> str:
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def write_version(v: str) -> None:
    VERSION_FILE.write_text(v + "\n", encoding="utf-8")


_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+].*)?$")


def bump(version: str, part: str) -> str:
    m = _SEMVER.match(version)
    if not m:
        raise SystemExit(f"Invalid semver in {VERSION_FILE}: '{version}'")
    major, minor, patch = map(int, m.groups()[:3])
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise SystemExit("Specify 'major', 'minor', or 'patch'")
    return f"{major}.{minor}.{patch}"


def release_changelog(new_version: str, entry: str | None) -> None:
    today = date.today().isoformat()
    if not CHANGELOG.exists():
        # create minimal changelog
        CHANGELOG.write_text(f"# Changelog\n\n## [Unreleased]\n\n\n\n## [{new_version}] - {today}\n- {entry or 'Initial release'}\n", encoding="utf-8")
        return

    text = CHANGELOG.read_text(encoding="utf-8")

    # Find Unreleased section (first occurrence)
    unreleased_header = "## [Unreleased]"
    if unreleased_header in text:
        before, after = text.split(unreleased_header, 1)
        # after starts with remainder; locate next section header
        # we'll move content up to the next '## [' or end
        m = re.search(r"\n## \[", after)
        if m:
            unreleased_content = after[: m.start()].strip()
            rest = after[m.start() :]
        else:
            unreleased_content = after.strip()
            rest = ""

        # compose new version section
        lines = []
        if unreleased_content:
            lines.append(unreleased_content)
        if entry:
            lines.append(f"- {entry}")
        if not lines:
            lines = ["- No change details provided"]

        new_section = f"\n## [{new_version}] - {today}\n" + "\n".join(lines) + "\n\n"

        # keep an Unreleased header at top (empty)
        new_text = before + unreleased_header + "\n\n" + rest
        # insert new_section after any leading frontmatter (we'll put it after the first '---' or directly after Unreleased block)
        new_text = new_text + "\n" + new_section
        CHANGELOG.write_text(new_text.strip() + "\n", encoding="utf-8")
    else:
        # No Unreleased header, just append
        append = f"\n## [{new_version}] - {today}\n- {entry or 'Initial release'}\n"
        CHANGELOG.write_text(text.rstrip() + "\n" + append + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print("Usage: bump_version.py [major|minor|patch] [optional changelog text]")
        raise SystemExit(2)
    part = argv[1]
    entry = " ".join(argv[2:]) if len(argv) > 2 else None

    current = read_version()
    new = bump(current, part)
    write_version(new)
    release_changelog(new, entry)
    print(f"Bumped {current} -> {new}")


if __name__ == "__main__":
    main(sys.argv)
