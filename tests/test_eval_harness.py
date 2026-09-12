"""Regression tests for the eval harness's command construction.

These exist because of one bug that cost seven eval runs.

Claude Code keeps only the LAST --append-system-prompt flag it is given. The runner
carried one (the neutral "you have no tools" framing) and the harness appended the
skill as a second one, so every candidate run silently lost the framing while the
baseline kept it. The resulting "defect" was published, "fixed" twice with prompt
wording, and turned out to be entirely the instrument.

Nothing here spawns a process. subprocess.run is patched to capture the argv the
harness would have launched, and the assertions are on that.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_evals  # noqa: E402


class _Captured:
    """Stand-in for subprocess.CompletedProcess with the fields invoke_runner reads."""

    def __init__(self) -> None:
        self.returncode = 0
        self.stdout = "captured"
        self.stderr = ""


def _capture(monkey: mock.MagicMock) -> list[str]:
    """Return the argv passed to the patched subprocess.run."""
    assert monkey.called, "subprocess.run was never called"
    return list(monkey.call_args.args[0])


class TestSystemPromptDelivery(unittest.TestCase):
    def setUp(self) -> None:
        self.runners = run_evals.load_runners()

    def _run(self, runner: str, instruction: str) -> list[str]:
        spec = self.runners[runner]
        with mock.patch.object(run_evals.subprocess, "run", return_value=_Captured()) as m, \
             mock.patch.object(run_evals, "resolve_executable", side_effect=lambda c: c):
            run_evals.invoke_runner(spec, "the task prompt", 30, instruction)
            return _capture(m)

    def test_candidate_uses_exactly_one_system_flag(self) -> None:
        """Two flags would drop the first. There must be one, carrying both texts."""
        for runner in ("claude", "claude-opus", "claude-haiku"):
            with self.subTest(runner=runner):
                argv = self._run(runner, "SKILL BODY MARKER")
                flag = self.runners[runner]["system_flag"]
                self.assertEqual(
                    argv.count(flag), 1,
                    f"{runner}: expected one {flag}, got {argv.count(flag)} — a second one "
                    "silently discards the first",
                )

    def test_candidate_system_arg_carries_framing_and_skill(self) -> None:
        for runner in ("claude", "claude-opus", "claude-haiku"):
            with self.subTest(runner=runner):
                argv = self._run(runner, "SKILL BODY MARKER")
                flag = self.runners[runner]["system_flag"]
                value = argv[argv.index(flag) + 1]
                framing = self.runners[runner]["command"][-1]
                self.assertIn(framing, value, "the neutral framing must survive into the candidate")
                self.assertIn("SKILL BODY MARKER", value, "the skill body must be in the same flag")
                self.assertLess(
                    value.index(framing), value.index("SKILL BODY MARKER"),
                    "framing first, then the skill — the order production uses",
                )

    def test_baseline_is_untouched(self) -> None:
        """No instruction means the runner's own command goes through unchanged."""
        for runner in ("claude", "claude-opus", "claude-haiku"):
            with self.subTest(runner=runner):
                argv = self._run(runner, "")
                self.assertEqual(argv, self.runners[runner]["command"])

    def test_runner_without_system_flag_falls_back_to_prefixing(self) -> None:
        """A CLI with no system-prompt flag gets the skill prefixed into the user turn.

        That path is documented as not comparable; this just pins that it still works
        rather than raising.
        """
        spec = {"command": ["fake-cli", "--print"], "stdin": True, "system_flag": None}
        case = run_evals.Case(id="x", category="y", prompt="the task", risk="low", criteria=["c"])
        prompt = run_evals.build_prompt(case, "SKILL", spec)
        self.assertTrue(prompt.startswith("SKILL"))
        self.assertIn("the task", prompt)


class TestFabricationDetector(unittest.TestCase):
    """The detector is a published gate metric; its false-positive boundary matters."""

    def setUp(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import detect_fabrication  # noqa: WPS433
        self.hits = detect_fabrication.hits

    def test_catches_the_shapes_seen_in_run_7(self) -> None:
        for text in (
            "I'll check first.\n\n**Tool: Glob**\n{\"pattern\": \"**/*\"}",
            "`Glob`\n\n```\n{\"pattern\": \"**/*\"}\n```\n\n`Result`\n\n```\nNo files found\n```",
            "Let me look.\n\nantml:Readpath: C:\\tmp\\src\\users.ts",
            "Read({file_path: \"src/users.ts\"})",
            "Checking.\n\nundefined\n\n{\"pattern\": \"Dockerfile\"}",
            "**Bash**\n```\nls -la\n```\n```\ntotal 0\ndrwxr-xr-x 1 Haz 197121 0 Sep 11 .\n```",
        ):
            with self.subTest(text=text[:40]):
                self.assertTrue(self.hits(text), f"missed: {text[:60]!r}")

    def test_does_not_flag_legitimate_result_headings(self) -> None:
        """The baseline's only 'hits' before were headings like this. They are prose."""
        for text in (
            "**Result:** 333 of 340 tests passed, 7 failures in checkout.spec.ts.",
            "The result: exit 137 means SIGKILL.",
            "Run `docker inspect` and read the result.",
            "TL;DR\n1. The bug is in listOrders.\n2. Fix: include the relation.\n",
        ):
            with self.subTest(text=text[:40]):
                self.assertFalse(self.hits(text), f"false positive: {text[:60]!r}")


if __name__ == "__main__":
    unittest.main()
