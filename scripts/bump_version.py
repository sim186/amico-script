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
import subprocess
import argparse
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

    # Find Unreleased section (first occurrence) with flexible header forms like
    # "## [Unreleased]", "[Unreleased]:", etc. If present, insert the new
    # release immediately after the top introductory text and leave the
    # Unreleased block intact (don't move its contents into the release).
    m_unrel = re.search(r"(?m)^(?:##\s*)?\[Unreleased\]\:?", text)
    if m_unrel:
        # Split intro (before the Unreleased header) and the remainder starting at Unreleased
        before = text[: m_unrel.start()]
        after = text[m_unrel.end():]

        # Extract the Unreleased block content up to the next top-level section (## [...) or EOF
        m_next = re.search(r"(?m)\n## \[", after)
        if m_next:
            unreleased_content = after[: m_next.start()].strip()
            rest = after[m_next.start():]
        else:
            unreleased_content = after.strip()
            rest = ""

        # Build lines: include existing Unreleased content first, then the provided entry
        lines: list[str] = []
        if unreleased_content:
            lines.append(unreleased_content)
        if entry:
            lines.append(f"- {entry}")
        if not lines:
            lines = ["- No change details provided"]

        new_section = f"\n## [{new_version}] - {today}\n" + "\n".join(lines) + "\n\n"

        # Replace the Unreleased header + its content with the new version section
        new_text = before.rstrip() + "\n\n" + new_section + rest.lstrip()
        CHANGELOG.write_text(new_text.strip() + "\n", encoding="utf-8")
    else:
        # No Unreleased header, just append
        append = f"\n## [{new_version}] - {today}\n- {entry or 'Initial release'}\n"
        CHANGELOG.write_text(text.rstrip() + "\n" + append + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Bump semantic version and update CHANGELOG.md")
    parser.add_argument("part", choices=("major", "minor", "patch"))
    parser.add_argument("entry", nargs="*", help="Optional changelog entry text")
    parser.add_argument("--create-tag", action="store_true", help="Create a git tag for the new version")
    parser.add_argument("--push", action="store_true", help="Push created tag to remote 'origin'")

    args = parser.parse_args(argv[1:])
    part = args.part
    entry = " ".join(args.entry) if args.entry else None

    current = read_version()
    new = bump(current, part)
    write_version(new)
    release_changelog(new, entry)
    print(f"Bumped {current} -> {new}")

    tag_name = f"v{new}"
    if args.create_tag:
        try:
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
            print(f"Created git tag {tag_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create git tag {tag_name}: {e}")
            raise SystemExit(1)

        if args.push:
            try:
                subprocess.run(["git", "push", "origin", tag_name], check=True)
                print(f"Pushed tag {tag_name} to origin")
            except subprocess.CalledProcessError as e:
                print(f"Failed to push tag {tag_name}: {e}")
                raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv)
