#!/usr/bin/env python3
"""Block .env and *.env from being committed; allow .env.example.

Usage:
  - Pre-commit (no args): check staged files (git diff --cached).
  - CI / PR (one arg = base ref, e.g. origin/homolog): check files changed in
    the diff base...HEAD.
Secret scanning validates content; this only prevents env file names.
"""

import re
import subprocess
import sys


def get_files_to_check(base_ref: str | None) -> list[str]:
    if base_ref is None:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
    else:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    return (result.stdout or "").strip().splitlines()


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else None
    paths = get_files_to_check(base_ref)

    # Block: exact ".env", any path ending with "/.env", or "*.env" (but not *.env.example)
    env_file = re.compile(r"^(.+/)?\.env$")
    env_extension = re.compile(r"^.+\.[eE][nN][vV]$")
    example_suffix = re.compile(r"\.env\.example$", re.IGNORECASE)

    for path in paths:
        if not path.strip():
            continue
        # Allow .env.example and any path ending with .env.example
        if example_suffix.search(path):
            continue
        # Block exact .env or path/.env
        if env_file.fullmatch(path):
            print(
                "pre-commit: cannot commit '.env' (contains secrets). "
                "Use .env.example for templates.",
                file=sys.stderr,
            )
            return 1
        # Block *.env (e.g. foo.env)
        if env_extension.match(path):
            print(
                f"pre-commit: cannot commit '{path}' (env file). "
                "Use .env.example for templates.",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
