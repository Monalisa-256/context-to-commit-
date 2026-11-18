from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PUBLICATION = Path(__file__).resolve().parents[1]


def reference_program() -> str:
    source = (PUBLICATION / "MASTERPLAN.md").read_text(encoding="utf-8")
    heading = "### 22.3 Complete `harness.py`"
    if source.count(heading) != 1:
        raise AssertionError("The reference section must be unique")
    part = source.split(heading, 1)[1]
    if "\n```python\n" not in part:
        raise AssertionError("Missing Python listing")
    code = part.split("\n```python\n", 1)[1].split("\n```\n", 1)[0]
    compile(code, "harness.py", "exec")
    return code.rstrip() + "\n"


def run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True,
                          capture_output=True, timeout=30)


class HarnessReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "reading-queue"
        self.repo.mkdir()
        (self.repo / "tests").mkdir()
        (self.repo / ".gitignore").write_text(
            ".worklog/\n__pycache__/\n*.pyc\n", encoding="utf-8"
        )
        (self.repo / "harness.py").write_text(
            reference_program(), encoding="utf-8"
        )
        (self.repo / "reading_queue.py").write_text(
            "class ReadingQueue:\n"
            "    def __init__(self):\n"
            "        self.books = {}\n"
            "        self.completed_count = 0\n"
            "    def add(self, key, title):\n"
            "        self.books[key] = {'title': title, 'done': False}\n"
            "    def complete(self, key):\n"
            "        self.books[key]['done'] = True\n"
            "        self.completed_count += 1\n",
            encoding="utf-8"
        )
        (self.repo / "tests" / "test_reading_queue.py").write_text(
            "import unittest\n"
            "from reading_queue import ReadingQueue\n"
            "class ReadingQueueTests(unittest.TestCase):\n"
            "    def test_repeated_completion(self):\n"
            "        q = ReadingQueue()\n"
            "        q.add('one', 'Example')\n"
            "        q.complete('one')\n"
            "        q.complete('one')\n"
            "        self.assertEqual(q.completed_count, 1)\n",
            encoding="utf-8"
        )
        self.git("init", "-q")
        self.git("config", "user.name", "Harness Test")
        self.git("config", "user.email", "harness@example.invalid")
        self.git("add", ".")
        self.git("commit", "-qm", "Record baseline")

    def git(self, *args: str):
        result = run(self.repo, "git", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def cli(self, *args: str):
        return run(self.repo, sys.executable, "harness.py", *args)

    def start(self):
        result = self.cli("start", "READ01", "--goal", "Fix repetition",
                          "--acceptance", "Repeated completion counts once")
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.repo.parent / "reading-queue_worktrees" / "READ01"

    def receipt(self):
        paths = sorted((self.repo / ".worklog" / "checks" / "READ01").glob("*.json"))
        self.assertTrue(paths, "Expected at least one receipt")
        return paths[-1], json.loads(paths[-1].read_text(encoding="utf-8"))

    def repair(self, tree: Path):
        source = tree / "reading_queue.py"
        text = source.read_text(encoding="utf-8")
        text = text.replace(
            "        self.books[key]['done'] = True\n"
            "        self.completed_count += 1\n",
            "        if not self.books[key]['done']:\n"
            "            self.books[key]['done'] = True\n"
            "            self.completed_count += 1\n"
        )
        source.write_text(text, encoding="utf-8")

    def test_baseline_reproduces_defect(self):
        result = run(self.repo, sys.executable, "-m", "unittest",
                     "discover", "-s", "tests", "-v")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stderr)

    def test_start_records_baseline_and_worktree(self):
        tree = self.start()
        self.assertTrue((tree / "reading_queue.py").is_file())
        task = json.loads((self.repo / ".worklog/tasks/READ01.json").read_text())
        self.assertEqual(task["id"], "READ01")
        self.assertEqual(task["base"], self.git("rev-parse", "HEAD"))
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_bad_task_identifier_rejected(self):
        result = self.cli("start", "../BAD", "--goal", "x", "--acceptance", "y")
        self.assertNotEqual(result.returncode, 0)

    def test_dirty_checkout_rejected(self):
        (self.repo / "reading_queue.py").write_text("# edited\n")
        result = self.cli("start", "READ01", "--goal", "x", "--acceptance", "y")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / ".worklog/tasks/READ01.json").exists())

    def test_context_has_sources_and_omission_section(self):
        self.start()
        result = self.cli("context", "READ01", "reading_queue.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        bundle = (self.repo / ".worklog/context/READ01.md").read_text()
        self.assertIn("Source SHA256:", bundle)
        self.assertIn("Omitted or incomplete sources", bundle)

    def test_sensitive_file_is_refused(self):
        tree = self.start()
        (tree / ".env").write_text("private=do-not-print\n")
        result = self.cli("context", "READ01", ".env")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("do-not-print", result.stdout + result.stderr)

    def test_symlink_source_is_refused(self):
        tree = self.start()
        target = Path(self.tmp.name) / "outside.txt"
        target.write_text("confidential\n")
        try:
            (tree / "outside_link.txt").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links are unavailable")
        result = self.cli("context", "READ01", "outside_link.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("confidential", result.stdout + result.stderr)

    def test_large_source_reports_truncation(self):
        tree = self.start()
        (tree / "large.txt").write_text("A" * 15000)
        result = self.cli("context", "READ01", "large.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        bundle = (self.repo / ".worklog/context/READ01.md").read_text()
        self.assertIn("Truncated: true", bundle)
        self.assertIn("partial excerpt", bundle)

    def test_failed_check_retains_failure_and_audit_fails(self):
        self.start()
        result = self.cli("check", "READ01")
        self.assertNotEqual(result.returncode, 0)
        _, receipt = self.receipt()
        self.assertEqual(receipt["test_outcome"], "failed")
        self.assertNotEqual(receipt["exit_code"], 0)
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

    def test_audit_without_check_fails(self):
        self.start()
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

    def test_pass_then_edit_invalidates_receipt(self):
        tree = self.start()
        self.repair(tree)
        self.assertEqual(self.cli("check", "READ01").returncode, 0)
        self.assertEqual(self.cli("audit", "READ01").returncode, 0)
        with (tree / "reading_queue.py").open("a") as stream:
            stream.write("\n# Later edit\n")
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

    def test_altered_stdout_is_rejected(self):
        tree = self.start()
        self.repair(tree)
        self.assertEqual(self.cli("check", "READ01").returncode, 0)
        _, receipt = self.receipt()
        out = self.repo / ".worklog/checks/READ01" / receipt["stdout"]
        out.write_text(out.read_text() + "tampered\n")
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

    def test_missing_stderr_is_rejected(self):
        tree = self.start()
        self.repair(tree)
        self.assertEqual(self.cli("check", "READ01").returncode, 0)
        _, receipt = self.receipt()
        (self.repo / ".worklog/checks/READ01" / receipt["stderr"]).unlink()
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)

    def test_mutating_failure_records_both_facts(self):
        tree = self.start()
        (tree / "tests" / "test_mutation.py").write_text(
            "import unittest\n"
            "from pathlib import Path\n"
            "class MutatingTest(unittest.TestCase):\n"
            "    def test_modify_then_fail(self):\n"
            "        p = Path('reading_queue.py')\n"
            "        p.write_text(p.read_text() + '\\n# changed\\n')\n"
            "        self.fail('controlled failing test')\n"
        )
        self.assertNotEqual(self.cli("check", "READ01").returncode, 0)
        _, receipt = self.receipt()
        self.assertEqual(receipt["test_outcome"], "failed")
        self.assertTrue(receipt["workspace_mutated"])

    def test_proposed_memory_preserves_state_and_source(self):
        self.start()
        result = self.cli("propose", "READ01", "--source", "reading_queue.py",
                          "--statement", "Repeat completion must be idempotent")
        self.assertEqual(result.returncode, 0, result.stderr)
        line = (self.repo / ".worklog/proposed_memories.jsonl").read_text().strip()
        record = json.loads(line)
        self.assertEqual(record["state"], "proposed")
        self.assertEqual(len(record["source_sha256"]), 64)

    def test_handoff_records_latest_check(self):
        tree = self.start()
        self.repair(tree)
        self.assertEqual(self.cli("check", "READ01").returncode, 0)
        self.assertEqual(self.cli("handoff", "READ01").returncode, 0)
        handoff = (self.repo / ".worklog/handoffs/READ01.md").read_text()
        self.assertIn("Applicability: True", handoff)
        self.assertIn("Test result: passed", handoff)

    def test_corrupt_task_record_rejected(self):
        self.start()
        (self.repo / ".worklog/tasks/READ01.json").write_text("{broken")
        self.assertNotEqual(self.cli("audit", "READ01").returncode, 0)


if __name__ == "__main__":
    unittest.main()
