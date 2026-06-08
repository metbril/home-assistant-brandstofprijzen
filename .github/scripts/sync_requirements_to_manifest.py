#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REQ_FILE = REPO_ROOT / "requirements.txt"
MANIFEST_FILE = REPO_ROOT / "custom_components" / "brandstofprijzen" / "manifest.json"


def parse_requirements(path):
    reqs = []
    if not path.exists():
        return reqs
    line_re = re.compile(r"^\s*([A-Za-z0-9_.+-]+)(?:\s*==\s*([^\s#]+))?")
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = line_re.match(line)
        if not m:
            continue
        name, ver = m.groups()
        reqs.append(f"{name}=={ver}" if ver else name)
    return reqs


def load_manifest(path):
    if not path.exists():
        print(f"Manifest not found at {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def write_manifest(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def git_commit_and_push(files, message):
    subprocess.check_call(["git", "add"] + files)
    subprocess.check_call(["git", "commit", "-m", message])
    subprocess.check_call(["git", "push"])


def main():
    reqs = parse_requirements(REQ_FILE)
    manifest = load_manifest(MANIFEST_FILE)

    current = manifest.get("requirements", [])
    if sorted(reqs) == sorted(current):
        print("manifest requirements already in sync.")
        return

    manifest["requirements"] = reqs
    write_manifest(MANIFEST_FILE, manifest)
    print("Updated manifest requirements to:", reqs)

    # Read from environment (set these in the GitHub Action step)
    message = os.getenv("COMMIT_MESSAGE", "Automated commit from workflow")
    name = os.getenv("COMMIT_NAME", "github-actions[bot]")
    email = os.getenv("COMMIT_EMAIL", "actions@github.com")

    # Prepare env for subprocess (works on Windows and Unix)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = name
    env["GIT_AUTHOR_EMAIL"] = email
    env["GIT_COMMITTER_NAME"] = name
    env["GIT_COMMITTER_EMAIL"] = email

    # Commit changes (optional: restrict to dependabot actor in CI)
    try:
        git_commit_and_push(
            [str(MANIFEST_FILE.relative_to(REPO_ROOT))],
            "Sync manifest.json requirements from requirements.txt",
        )
    except subprocess.CalledProcessError as e:
        print("Git commit/push failed:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
