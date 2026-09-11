"""Behavioural tests for the always-on SessionStart hooks.

Three implementations of the same behaviour ship in `hooks/` — Node, POSIX sh,
and PowerShell. They must agree, because a user who installs on Windows and a
user who installs on Linux are promised the same ruleset.

Every test here asserts one of three things:

    1. The hook stays silent unless the user opted in. It is opt-in by design.
    2. When it fires, it emits the skill body with the YAML frontmatter stripped.
    3. It never blocks session start, whatever goes wrong.

The sh and PowerShell tests skip when their interpreter is unavailable rather
than failing, so the suite runs on any platform.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS = REPO_ROOT / "hooks"
SKILL = REPO_ROOT / "skills" / "tldr" / "SKILL.md"

NODE = shutil.which("node")
SH = shutil.which("sh") or shutil.which("bash")
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


def run_hook(command: list[str], config_dir: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
    # encoding is explicit: subprocess's text=True decodes with the locale codepage
    # on Windows, which mangles the skill's non-ASCII punctuation. The hooks emit UTF-8.
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        env=env,
    )


class HookBehaviourMixin:
    """Shared assertions, parameterised by implementation."""

    command: list[str]

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.config_dir = Path(self._tmp.name)
        self.flag = self.config_dir / ".tldr-always"
        self.addCleanup(self._tmp.cleanup)

    def test_silent_without_the_flag(self) -> None:
        result = run_hook(self.command, self.config_dir)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "", "hook spoke without an opt-in flag")

    def test_emits_ruleset_when_flag_exists(self) -> None:
        self.flag.write_text("", encoding="utf-8")
        result = run_hook(self.command, self.config_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn("TLDR MODE ACTIVE", result.stdout)
        self.assertIn("Demote, don't delete", result.stdout)
        self.assertIn("Never compress these", result.stdout)

    def test_strips_yaml_frontmatter(self) -> None:
        """The frontmatter is harness metadata, not instructions for the model."""
        self.flag.write_text("", encoding="utf-8")
        result = run_hook(self.command, self.config_dir)

        self.assertNotIn("disable-model-invocation", result.stdout)
        self.assertNotIn("metadata:", result.stdout)

    def test_reports_the_configured_depth(self) -> None:
        self.flag.write_text("1", encoding="utf-8")
        result = run_hook(self.command, self.config_dir)
        self.assertIn("Depth dial is set to 1", result.stdout)

    def test_falls_back_to_default_depth_on_garbage(self) -> None:
        self.flag.write_text("banana", encoding="utf-8")
        result = run_hook(self.command, self.config_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Depth dial is set to 3", result.stdout)

    def test_never_blocks_session_start(self) -> None:
        """Whatever is wrong, exit 0. A broken hook must not break the session."""
        self.flag.write_text("\x00\xff not a depth \n\n", encoding="utf-8", errors="ignore")
        result = run_hook(self.command, self.config_dir)
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipUnless(NODE, "node is not installed")
class TestNodeHook(HookBehaviourMixin, unittest.TestCase):
    @property
    def command(self) -> list[str]:
        return [NODE, str(HOOKS / "always-on.mjs")]


@unittest.skipUnless(SH, "sh is not installed")
class TestShellHook(HookBehaviourMixin, unittest.TestCase):
    @property
    def command(self) -> list[str]:
        return [SH, str(HOOKS / "always-on.sh")]


@unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
class TestPowerShellHook(HookBehaviourMixin, unittest.TestCase):
    @property
    def command(self) -> list[str]:
        return [POWERSHELL, "-NoProfile", "-File", str(HOOKS / "always-on.ps1")]


class TestImplementationsAgree(unittest.TestCase):
    """The three hooks must emit the same ruleset body, byte for byte."""

    def _body(self, command: list[str]) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp)
            (config_dir / ".tldr-always").write_text("", encoding="utf-8")
            stdout = run_hook(command, config_dir).stdout
        # Drop the header line; keep the ruleset that follows it.
        _, _, body = stdout.partition("\n\n")
        return body.strip().replace("\r\n", "\n")

    @unittest.skipUnless(NODE and SH, "need both node and sh")
    def test_node_and_sh_agree(self) -> None:
        self.assertEqual(
            self._body([NODE, str(HOOKS / "always-on.mjs")]),
            self._body([SH, str(HOOKS / "always-on.sh")]),
        )

    @unittest.skipUnless(NODE and POWERSHELL, "need both node and PowerShell")
    def test_node_and_powershell_agree(self) -> None:
        self.assertEqual(
            self._body([NODE, str(HOOKS / "always-on.mjs")]),
            self._body([POWERSHELL, "-NoProfile", "-File", str(HOOKS / "always-on.ps1")]),
        )

    @unittest.skipUnless(NODE, "node is not installed")
    def test_body_matches_the_canonical_skill(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        expected = skill.split("---", 2)[2].strip().replace("\r\n", "\n")
        self.assertEqual(self._body([NODE, str(HOOKS / "always-on.mjs")]), expected)


if __name__ == "__main__":
    unittest.main()
