#!/usr/bin/env python3
"""Check Git index contents (all tracked files, or only staged changes).

Untracked files and unstaged worktree edits are not inspected. This is an
accidental-leak guard, not a complete secret scanner; contents are never printed.
"""
import argparse
import pathlib
import re
import subprocess
import sys

PRIVATE_DIRS = {"data", "media", "secrets", "credentials", "browser-profiles",
                "runtime-data", "backups", "private", "omnifeed-private"}
PRIVATE_NAMES = {"playback-history.json", "history.json", "cookies.json",
                 "storage-state.json", "storagestate.json", ".env", "config.local.json",
                 "credentials.json", "secrets.json", "tokens.json", ".netrc"}
PRIVATE_SUFFIXES = {".sqlite", ".sqlite3", ".db", ".pem", ".key", ".p12",
                    ".mp4", ".mp3", ".flac", ".m4a", ".wav", ".mov"}
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
]


def problems(name, content):
    path = pathlib.PurePosixPath(name.lower())
    if (PRIVATE_DIRS.intersection(path.parts) or path.name in PRIVATE_NAMES
            or (path.name.startswith(".env.") and path.name != ".env.example")
            or path.suffix.lower() in PRIVATE_SUFFIXES
            or any(path.name.endswith(ext + sidecar)
                   for ext in (".db", ".sqlite", ".sqlite3")
                   for sidecar in ("-wal", "-shm", "-journal"))):
        return ["private/runtime file path"]
    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        return ["possible credential"]
    return []


def run(staged=False):
    command = (["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
               if staged else ["git", "ls-files", "-z"])
    names = subprocess.check_output(command).decode().split("\0")
    failures = []
    for name in filter(None, names):
        path_issues = problems(name, b"")
        if path_issues:
            failures.extend((name, issue) for issue in path_issues)
            continue
        # Inspect the index, not the worktree: staged contents are what get committed.
        content = subprocess.check_output(["git", "show", ":" + name])
        failures.extend((name, issue) for issue in problems(name, content))
    for name, issue in failures:
        print(f"Blocked: {name}: {issue}", file=sys.stderr)
    if failures:
        return 1
    print("Public-file check passed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    sys.exit(run(args.staged))
