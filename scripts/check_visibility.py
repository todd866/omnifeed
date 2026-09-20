#!/usr/bin/env python3
"""Fail closed if a GitHub repository does not have the required visibility."""
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", help="GitHub OWNER/REPO or URL")
    parser.add_argument("expected", choices=("PRIVATE", "PUBLIC"))
    args = parser.parse_args()
    result = subprocess.run(
        ["gh", "repo", "view", args.repository, "--json", "visibility", "--jq", ".visibility"],
        capture_output=True, text=True, timeout=30)
    if result.returncode:
        print("Visibility check failed: GitHub query unavailable; check authentication and network.", file=sys.stderr)
        return 1
    if result.stdout.strip() != args.expected:
        print("Visibility check failed: repository is not " + args.expected, file=sys.stderr)
        return 1
    print("Repository visibility verified: " + args.expected)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, subprocess.TimeoutExpired):
        print("Visibility check failed: GitHub query timed out or the CLI is unavailable.", file=sys.stderr)
        sys.exit(1)
