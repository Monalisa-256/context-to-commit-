"""Verify that the published example is usable without editing this repository."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "reading_queue"
SYSCALL_TIMEOUT = 45


def run(cwd: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          timeout=SYSCALL_TIMEOUT, check=False)


class PublishedExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="context-to-commit-")
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name) / "reading-queue-lab"

    def bootstrap(self) -> None:
        result = run(ROOT, sys.executable,
                     str(EXAMPLE / "bootstrap.py"), str(self.lab))
        self.assertEqual(result.returncode, 0, result.stderr)

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(self.lab, sys.executable, "harness.py", *args)

    def start(self) -> Path:
        result = self.cli("start", "READ01", "--goal", "Fix repeated count",
                          "--acceptance", "Completion counts a book once")
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.lab.parent / "reading-queue-lab_worktrees" / "READ01"

    def test_extracted_program_matches_document(self):
        result = run(ROOT, sys.executable,
                     str(ROOT / "tools" / "sync_reference.py"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_example_starts_with_real_failure(self):
        self.bootstrap()
        outcome = run(self.lab, sys.executable, "-m", "unittest", "discover",
                      "-s", "tests", "-v")
        self.assertNotEqual(outcome.returncode, 0)
        self.assertIn("test_completion_is_idempotent", outcome.stderr)
        self.assertIn("FAIL", outcome.stderr)

    def test_bootstrap_refuses_to_replace_existing_data(self):
        self.lab.mkdir()
        (self.lab / "important.txt").write_text("preserve me", encoding="utf-8")
        result = run(ROOT, sys.executable,
                     str(EXAMPLE / "bootstrap.py"), str(self.lab))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.lab / "important.txt").read_text(), "preserve me")

    def test_complete_workflow_and_invalidated_evidence(self):
        self.bootstrap()
        tree = self.start()
        self.assertEqual(self.cli("context", "READ01", "reading_queue.py",
                                  "tests/test_reading_queue.py").returncode, 0)
        self.assertNotEqual(self.cli("check", "READ01").returncode, 0)
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

        # Apply the same conditional increment shown in MASTERPLAN.md.
        implementation = tree / "reading_queue.py"
        source = implementation.read_text(encoding="utf-8")
        old = '        book["done"] = True\n        self.completed_count += 1'
        new = ('        if not book["done"]:\n'
               '            book["done"] = True\n'
               '            self.completed_count += 1')
        self.assertIn(old, source)
        implementation.write_text(source.replace(old, new), encoding="utf-8")
        self.assertEqual(self.cli("check", "READ01").returncode, 0)
        self.assertEqual(self.cli("audit", "READ01").returncode, 0)
        self.assertEqual(self.cli("handoff", "READ01").returncode, 0)
        handoff = (self.lab / ".worklog" / "handoffs" / "READ01.md").read_text()
        self.assertIn("Applicability: True", handoff)
        self.assertIn("Test result: passed", handoff)

        implementation.write_text(implementation.read_text() + "\n# changed later\n")
        stale = self.cli("audit", "READ01")
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("workspace differs", stale.stdout)

    def test_untrusted_source_path_denied(self):
        self.bootstrap()
        self.start()
        result = self.cli("context", "READ01", "../outside-secret.txt")
        self.assertNotEqual(result.returncode, 0)

    def test_main_checkout_remains_clean(self):
        self.bootstrap()
        self.start()
        result = run(self.lab, "git", "status", "--porcelain")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_proposed_memory_does_not_claim_approval(self):
        self.bootstrap()
        self.start()
        proposed = self.cli("propose", "READ01", "--source",
                            "reading_queue.py", "--statement",
                            "Duplicate completion should not increase count")
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        p = self.lab / ".worklog" / "proposed_memories.jsonl"
        entry = json.loads(p.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(entry["state"], "proposed")
        self.assertEqual(entry["task_id"], "READ01")


if __name__ == "__main__":
    unittest.main()
