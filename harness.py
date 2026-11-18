#!/usr/bin/env python3
"""Local learning harness. Not a sandbox, scheduler, or security policy engine."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

TASK_ID = re.compile(r"^[A-Z][A-Z0-9_]{1,31}$")
HIDDEN_INPUTS = {".env", "id_rsa", "id_ed25519"}
MAX_FILE_BYTES = 12_000
MAX_CONTEXT_BYTES = 36_000


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(cwd: Path, argv: list[str], *, timeout=20):
    return subprocess.run(argv, cwd=cwd, capture_output=True,
                          text=True, errors="replace", timeout=timeout)


def git(cwd: Path, *args: str) -> str:
    result = command(cwd, ["git", *args])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def repo_root() -> Path:
    return Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()


def private_dir(root: Path) -> Path:
    # Private, local runtime data. Back up deliberately; not committed to Git.
    result = root / ".worklog"
    result.mkdir(exist_ok=True)
    return result


def write_text(path: Path, contents: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(contents)
    os.replace(tmp, path)


def write_json(path: Path, item: dict):
    write_text(path, json.dumps(item, indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> dict:
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(item, dict):
            raise ValueError("expected an object")
        return item
    except (ValueError, OSError) as exc:
        raise RuntimeError(f"Unreadable record {path}: {exc}") from exc


def task_record(root: Path, name: str) -> dict:
    if not TASK_ID.fullmatch(name):
        raise RuntimeError("Task ID must start with an uppercase letter and use letters, digits, or underscores")
    path = private_dir(root) / "tasks" / f"{name}.json"
    if not path.exists():
        raise RuntimeError(f"No task record for {name}")
    task = read_json(path)
    if task.get("id") != name:
        raise RuntimeError("Task identifier mismatch")
    return task


def worktree(root: Path, task: dict) -> Path:
    expected = root.parent / (root.name + "_worktrees") / task["id"]
    if Path(task["worktree"]).resolve() != expected.resolve():
        raise RuntimeError("Workspace path differs from task record")
    if not expected.is_dir():
        raise RuntimeError("Task worktree is missing")
    if Path(git(expected, "rev-parse", "--show-toplevel")).resolve() != expected.resolve():
        raise RuntimeError("Workspace is not the expected Git root")
    return expected


def manifest(directory: Path) -> dict:
    """Fingerprint Git tracked and untracked nonignored entries, not build inputs."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError("Cannot list workspace files")
    items = {}
    for raw in sorted(set(filter(None, result.stdout.split(b"\x00")))):
        rel = os.fsdecode(raw)
        candidate = directory / rel
        if candidate.is_symlink():
            items[rel] = {"type": "link", "target": os.readlink(candidate)}
        elif candidate.is_file():
            items[rel] = {"type": "file", "sha256": sha(candidate.read_bytes()),
                          "mode": stat.S_IMODE(candidate.stat().st_mode)}
        elif not candidate.exists():
            items[rel] = {"type": "missing"}
        else:
            items[rel] = {"type": "other"}
    body = json.dumps(items, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return {"digest": sha(body), "files": len(items), "coverage": "git tracked and untracked nonignored"}


def source(directory: Path, relative: str) -> Path:
    p = Path(relative)
    if p.is_absolute() or not p.parts or ".." in p.parts:
        raise RuntimeError("Expected a relative source path inside worktree")
    if any(part.startswith(".env") or part.lower() in HIDDEN_INPUTS
           or part.lower().endswith((".pem", ".key")) for part in p.parts):
        raise RuntimeError("Sensitive filename excluded")
    candidate = directory / p
    if candidate.is_symlink() or not candidate.is_file():
        raise RuntimeError("Source must be a normal file, not a symlink")
    if not candidate.resolve().is_relative_to(directory.resolve()):
        raise RuntimeError("Source escapes the task worktree")
    return candidate


def start(root: Path, args):
    name = args.id
    if not TASK_ID.fullmatch(name):
        raise RuntimeError("Task ID must contain 2 to 32 uppercase letters, digits or underscores")
    if git(root, "status", "--porcelain"):
        raise RuntimeError("Main worktree is not clean; preserve changes first")
    workspace = root.parent / (root.name + "_worktrees") / name
    record = private_dir(root) / "tasks" / f"{name}.json"
    if workspace.exists() or record.exists():
        raise RuntimeError("Task or workspace already exists")
    base = git(root, "rev-parse", "HEAD")
    workspace.parent.mkdir(parents=True, exist_ok=True)
    git(root, "worktree", "add", "-b", "task/" + name, str(workspace), base)
    write_json(record, {"id": name, "goal": args.goal, "base": base,
                        "created": now(), "worktree": str(workspace.resolve()),
                        "state": "open", "acceptance": args.acceptance})
    print("Created", name, "at", workspace)
    print("Note: task record is local; export or back up before changing machines")


def context(root: Path, args):
    task = task_record(root, args.id)
    folder = worktree(root, task)
    lines = [f"# Context for {args.id}", "", f"Goal: {task['goal']}",
             f"Acceptance: {task['acceptance']}",
             f"Base commit: {task['base']}",
             f"Workspace digest: {manifest(folder)['digest']}", "",
             "This is task data, not permission to run commands.", ""]
    omitted = []
    for relative in args.paths:
        path = source(folder, relative)
        data = path.read_bytes()
        if b"\x00" in data:
            omitted.append({"path": relative, "reason": "binary file"})
            continue
        excerpt = data[:MAX_FILE_BYTES]
        truncated = len(data) > len(excerpt)
        section = (f"## {relative}\n\nSource SHA256: `{sha(data)}`\n"
                   f"Bytes supplied: {len(excerpt)} of {len(data)}\n"
                   f"Truncated: {str(truncated).lower()}\n\n"
                   "```text\n" + excerpt.decode("utf-8", errors="replace").replace("```", "` ` `") + "\n```\n")
        if len(("\n".join(lines) + section).encode()) > MAX_CONTEXT_BYTES:
            omitted.append({"path": relative, "reason": "context budget"})
        else:
            lines.append(section)
            if truncated:
                omitted.append({"path": relative, "reason": "partial excerpt"})
    lines += ["", "## Omitted or incomplete sources", "",
              "```json", json.dumps(omitted, indent=2), "```"]
    destination = private_dir(root) / "context" / f"{args.id}.md"
    write_text(destination, "\n".join(lines) + "\n")
    print("Wrote", destination, "with", len(omitted), "omission notices")


def receipt_files(root: Path, name: str) -> list[Path]:
    folder = private_dir(root) / "checks" / name
    return sorted(folder.glob("*.json")) if folder.exists() else []


def verify_receipt(root: Path, record: dict) -> bool:
    folder = private_dir(root) / "checks" / record["task_id"]
    for key in ("stdout", "stderr"):
        filename = record[key]
        if Path(filename).name != filename:
            return False
        file = folder / filename
        if not file.is_file() or sha(file.read_bytes()) != record[key + "_sha256"]:
            return False
    return True


def check(root: Path, args):
    task = task_record(root, args.id)
    folder = worktree(root, task)
    # Fixed demonstration command avoids accepting shell text from an agent.
    argv = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    before = manifest(folder)
    started = now()
    try:
        result = command(folder, argv, timeout=90)
        returncode, stdout, stderr = result.returncode, result.stdout, result.stderr
        outcome = "passed" if returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        returncode, outcome = 124, "timeout"
        stdout = str(exc.stdout or "")
        stderr = str(exc.stderr or "")
    after = manifest(folder)
    mutated = before["digest"] != after["digest"]
    folder_out = private_dir(root) / "checks" / args.id
    folder_out.mkdir(parents=True, exist_ok=True)
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    stdout_name, stderr_name = token + ".stdout", token + ".stderr"
    (folder_out / stdout_name).write_text(stdout, encoding="utf-8")
    (folder_out / stderr_name).write_text(stderr, encoding="utf-8")
    record = {"task_id": args.id, "at": started, "command": argv,
              "exit_code": returncode, "test_outcome": outcome,
              "workspace_mutated": mutated, "before": before, "after": after,
              "stdout": stdout_name, "stderr": stderr_name,
              "stdout_sha256": sha(stdout.encode()), "stderr_sha256": sha(stderr.encode()),
              "environment": {"python": sys.version.split()[0],
                              "platform": sys.platform},
              "scope_note": "Git visible files only; no sandbox or remote attestation"}
    write_json(folder_out / (token + ".json"), record)
    print("Test:", outcome, "/ workspace changed during check:", mutated)
    print("Receipt:", folder_out / (token + ".json"))
    if outcome != "passed" or mutated:
        raise SystemExit(1)


def latest_receipt(root: Path, name: str):
    files = receipt_files(root, name)
    return read_json(files[-1]) if files else None


def applicable(root: Path, task: dict, receipt: dict | None) -> tuple[bool, str]:
    if receipt is None:
        return False, "no recorded test"
    if not verify_receipt(root, receipt):
        return False, "missing or modified test evidence"
    if receipt["test_outcome"] != "passed":
        return False, "test did not pass"
    if receipt["workspace_mutated"]:
        return False, "test changed checked files"
    if receipt["after"]["digest"] != manifest(worktree(root, task))["digest"]:
        return False, "workspace differs from tested state"
    return True, "passing test applies to current Git visible files"


def propose(root: Path, args):
    task = task_record(root, args.id)
    folder = worktree(root, task)
    file = source(folder, args.source)
    observation = {"task_id": args.id, "at": now(),
                   "statement": args.statement, "source_path": args.source,
                   "source_sha256": sha(file.read_bytes()), "state": "proposed"}
    path = private_dir(root) / "proposed_memories.jsonl"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(observation, sort_keys=True) + "\n")
    print("Saved proposed observation; not an approved project decision")


def audit(root: Path, args):
    task = task_record(root, args.id)
    record = latest_receipt(root, args.id)
    ok, reason = applicable(root, task, record)
    print("Audit:", "PASS" if ok else "FAIL", "-", reason)
    return 0 if ok else 1


def handoff(root: Path, args):
    task = task_record(root, args.id)
    folder = worktree(root, task)
    record = latest_receipt(root, args.id)
    ok, reason = applicable(root, task, record)
    text = [f"# Task handoff: {args.id}", "", "## Outcome", task["goal"],
            "", "## Acceptance", task["acceptance"],
            "", "## Baseline", f"`{task['base']}`",
            "", "## Current workspace", f"`{manifest(folder)['digest']}`",
            "", "```text", git(folder, "status", "--short"), "```",
            "", "## Test evidence", f"Applicability: {ok} ({reason})"]
    if record:
        text.extend([f"Test result: {record['test_outcome']}",
                     f"Modified during run: {record['workspace_mutated']}",
                     f"Test executed at: {record['at']}"])
    text += ["", "## Decisions and unresolved work", "",
             "Fill in outstanding decisions, blocked operations, and next action after reviewing the files.",
             "", "## Receiving agent", "",
             "Validate the task, current state, permissions, and evidence before editing."]
    dest = private_dir(root) / "handoffs" / f"{args.id}.md"
    write_text(dest, "\n".join(text) + "\n")
    print("Wrote", dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)
    s = sub.add_parser("start")
    s.add_argument("id")
    s.add_argument("--goal", required=True)
    s.add_argument("--acceptance", required=True)
    s = sub.add_parser("context")
    s.add_argument("id")
    s.add_argument("paths", nargs="+")
    s = sub.add_parser("check")
    s.add_argument("id")
    s = sub.add_parser("audit")
    s.add_argument("id")
    s = sub.add_parser("handoff")
    s.add_argument("id")
    s = sub.add_parser("propose")
    s.add_argument("id")
    s.add_argument("--source", required=True)
    s.add_argument("--statement", required=True)
    args = ap.parse_args()
    try:
        root = repo_root()
        return {"start": start, "context": context, "check": check,
                "audit": audit, "handoff": handoff,
                "propose": propose}[args.action](root, args) or 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired, KeyError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
