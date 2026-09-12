"""Contract tests for the repository itself.

These guard the invariants that break silently: a mirror drifting from the
canonical skill, a version bumped in one manifest but not the others, a README
install table pointing at an INSTALL.md anchor that no longer exists.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "tldr" / "SKILL.md"
REFERENCE = REPO_ROOT / "skills" / "tldr" / "reference.md"
README = REPO_ROOT / "README.md"
INSTALL = REPO_ROOT / "INSTALL.md"

VERSIONED_MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    "qwen-extension.json",
    "kimi.plugin.json",
    "package.json",
]

ALL_MANIFESTS = VERSIONED_MANIFESTS + [
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    "plugin.json",
    "opencode.json",
    "hooks/hooks.json",
    "evals/runners.example.json",
]


def relative(entry: str) -> str:
    """Strip a leading "./" without str.lstrip's character-set semantics."""
    return entry[2:] if entry.startswith("./") else entry


def anchor(heading: str) -> str:
    """GitHub's heading-to-anchor slug."""
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    # GitHub replaces each whitespace character with a hyphen rather than
    # collapsing runs, so "Cline / Roo Code" becomes "cline--roo-code".
    return re.sub(r"\s", "-", slug)


class TestManifests(unittest.TestCase):
    def test_every_manifest_is_valid_json(self) -> None:
        for rel in ALL_MANIFESTS:
            with self.subTest(manifest=rel):
                path = REPO_ROOT / rel
                self.assertTrue(path.exists(), f"{rel} is missing")
                json.loads(path.read_text(encoding="utf-8"))

    def test_versions_are_aligned(self) -> None:
        versions = {}
        for rel in VERSIONED_MANIFESTS:
            data = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
            versions[rel] = data.get("version")

        distinct = set(versions.values())
        self.assertEqual(
            len(distinct),
            1,
            f"manifest versions have drifted: {json.dumps(versions, indent=2)}",
        )
        self.assertIsNotNone(distinct.pop(), "manifests are missing a version")

    def test_plugin_names_are_consistent(self) -> None:
        # package.json is an npm manifest and "tldr" is already taken on npm by the
        # tldr-pages client, so it alone uses a suffixed name.
        for rel in ALL_MANIFESTS:
            if rel == "package.json":
                continue
            data = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
            if "name" in data:
                with self.subTest(manifest=rel):
                    self.assertEqual(data["name"], "tldr", f"{rel} names the plugin wrongly")

    def test_referenced_paths_exist(self) -> None:
        """A manifest pointing at a file that does not exist is a broken install."""
        checks = [
            (".codex-plugin/plugin.json", "skills", "./skills/"),
            ("kimi.plugin.json", "skills", "./skills/"),
        ]
        for rel, key, expected in checks:
            data = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
            with self.subTest(manifest=rel):
                self.assertEqual(data.get(key), expected)
                self.assertTrue((REPO_ROOT / "skills").is_dir())

        opencode = json.loads((REPO_ROOT / "opencode.json").read_text(encoding="utf-8"))
        for entry in opencode["plugin"]:
            with self.subTest(plugin=entry):
                self.assertTrue((REPO_ROOT / relative(entry)).exists(), entry)

        package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        for section in ("pi", "omp"):
            for entry in package[section].get("extensions", []):
                with self.subTest(extension=entry):
                    self.assertTrue((REPO_ROOT / relative(entry)).exists(), entry)


class TestSkillContract(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL.read_text(encoding="utf-8")

    def test_has_frontmatter_with_required_keys(self) -> None:
        self.assertTrue(self.text.startswith("---\n"), "SKILL.md must open with frontmatter")
        frontmatter = self.text.split("---", 2)[1]
        for key in ("name:", "description:", "license:"):
            with self.subTest(key=key):
                self.assertIn(key, frontmatter)
        self.assertRegex(
            frontmatter, r"(?m)^name:\s*tldr\s*$", msg="skill name must be 'tldr'"
        )

    def test_declares_the_core_contract(self) -> None:
        """The one guarantee the whole project rests on."""
        self.assertIn("Demote, don't delete", self.text)
        self.assertIn("must not end up with a false belief", self.text)

    def test_has_a_never_compress_section(self) -> None:
        self.assertIn("## Never compress these", self.text)

        section = self.text.split("## Never compress these", 1)[1].split("\n## ", 1)[0]
        for required in (
            "Destructive actions",
            "Security findings",
            "data loss",
            "Verbatim error text",
            "Diffs",
        ):
            with self.subTest(item=required):
                self.assertIn(required, section, f"never-compress list is missing: {required}")

    def test_documents_both_render_surfaces(self) -> None:
        """A raw <details> tag in a terminal is worse than no fold at all."""
        self.assertIn("<details>", self.text)
        self.assertIn("--- detail ---", self.text)

    def test_documents_the_agent_to_agent_block(self) -> None:
        self.assertIn("## Agent-to-agent mode", self.text)
        section = self.text.split("## Agent-to-agent mode", 1)[1]
        for key in ("status:", "summary:", "next:", "full:"):
            with self.subTest(key=key):
                self.assertIn(key, section)

    def test_depth_dial_values_match_the_adapters(self) -> None:
        for depth in ("/tldr 0", "/tldr 1", "/tldr 3", "/tldr 5", "/tldr full"):
            with self.subTest(depth=depth):
                self.assertIn(depth, self.text)

    def test_stop_phrases_match_the_adapters(self) -> None:
        """The extension hard-codes these; the skill must teach the same ones."""
        extension = (REPO_ROOT / "extensions" / "tldr.ts").read_text(encoding="utf-8")
        for phrase in ("stop tldr", "tldr off", "normal mode"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text, f"SKILL.md does not document {phrase!r}")
                self.assertIn(phrase, extension, f"extensions/tldr.ts does not handle {phrase!r}")


class TestCoreReferenceSplit(unittest.TestCase):
    """SKILL.md is the core the model reads every turn; reference.md is the rest.

    The core was 18k characters and 46 bold phrases before the split. Always-on
    harnesses re-send it on every call, so its size is a per-turn tax on every
    user. These bounds are the split's design constraints, pinned so the core
    cannot regrow one "just one more rule" at a time.
    """

    CORE_MAX_CHARS = 5_000
    MAX_BOLD = 10
    MAX_NEVER = 10

    def setUp(self) -> None:
        self.core = SKILL.read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_reference_file_exists_and_is_linked_from_the_core(self) -> None:
        self.assertTrue(REFERENCE.exists(), "skills/tldr/reference.md is missing")
        self.assertIn(
            "reference.md", self.core,
            "the core must point at reference.md so on-demand loaders can find it",
        )

    def test_core_stays_under_the_size_budget(self) -> None:
        self.assertLessEqual(
            len(self.core), self.CORE_MAX_CHARS,
            f"SKILL.md is {len(self.core)} chars; the budget is {self.CORE_MAX_CHARS}. "
            "Move elaboration and examples to reference.md.",
        )

    def test_core_uses_emphasis_sparingly(self) -> None:
        bold = re.findall(r"\*\*[^*\n]+\*\*", self.core)
        self.assertLessEqual(
            len(bold), self.MAX_BOLD,
            f"{len(bold)} bold phrases; when everything is emphasised nothing is",
        )

    def test_core_does_not_lean_on_never(self) -> None:
        nevers = re.findall(r"\bnever\b", self.core, flags=re.IGNORECASE)
        self.assertLessEqual(
            len(nevers), self.MAX_NEVER,
            f"{len(nevers)} uses of 'never'; prefer stating what to do",
        )

    def test_core_lists_all_eight_never_compress_items(self) -> None:
        section = self.core.split("## Never compress these", 1)[1].split("\n## ", 1)[0]
        items = re.findall(r"(?m)^\s*\d+\.\s", section)
        self.assertEqual(len(items), 8, "the never-compress list must ship complete in the core")

    def test_core_does_not_instruct_actions(self) -> None:
        """The skill shapes output. Whether to act is the harness's decision.

        Every phrase here was in the 18k version and was either a tool-use policy
        or an instruction to write files, which the eval could not exercise and
        which the harness may forbid.
        """
        for phrase in (
            "write it to a file",
            "belongs in a file",
            "confirm before acting",
            "Check the message before reaching",
        ):
            with self.subTest(phrase=phrase):
                # assertNotIn would print the whole 5k file on failure; keep it short.
                self.assertFalse(phrase in self.core, f"core instructs an action: {phrase!r}")

    def test_reference_does_not_redefine_the_contract(self) -> None:
        """One source of truth for the rules that matter; the reference elaborates."""
        reference = REFERENCE.read_text(encoding="utf-8")
        self.assertNotIn("## Never compress these", reference)
        self.assertNotIn("name: tldr", reference, "reference.md must not carry skill frontmatter")


class TestMirrors(unittest.TestCase):
    def test_mirrors_are_in_sync(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "check_mirrors.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestInstallDocs(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = README.read_text(encoding="utf-8")
        self.install = INSTALL.read_text(encoding="utf-8")
        self.anchors = {
            anchor(m) for m in re.findall(r"^#{2,3}\s+(.+)$", self.install, re.M)
        }

    def test_readme_install_links_resolve(self) -> None:
        links = re.findall(r"\]\(INSTALL\.md#([\w-]+)\)", self.readme)
        self.assertTrue(links, "README has no INSTALL.md deep links")
        for link in links:
            with self.subTest(anchor=link):
                self.assertIn(link, self.anchors, f"INSTALL.md has no heading for #{link}")

    def test_install_covers_every_agent_in_the_readme_table(self) -> None:
        table = self.readme.split("## Supported agents", 1)[1].split("\n## ", 1)[0]
        rows = re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|", table, re.M)
        self.assertGreaterEqual(len(rows), 12, "expected the full supported-agents table")

    def test_repo_slug_is_consistent(self) -> None:
        """A stale owner/repo slug is a broken install command."""
        for path in (README, INSTALL, REPO_ROOT / "AGENTS.md"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.name):
                self.assertNotIn("ayghri/", text, "reference repo slug leaked into docs")
                if "github.com/" in text:
                    self.assertIn("SurefireStudios/tldr", text)


class TestEvalCases(unittest.TestCase):
    def test_cases_validate(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "run_evals.py"), "validate"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hard_block_categories_have_cases(self) -> None:
        """The release gate is scoped to these categories; they must not be empty."""
        cases = [
            json.loads(line)
            for line in (REPO_ROOT / "evals" / "cases.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        categories = {case["category"] for case in cases}
        for required in ("never-compress", "safety", "agent-to-agent", "fidelity"):
            with self.subTest(category=required):
                self.assertIn(required, categories)


if __name__ == "__main__":
    unittest.main()
