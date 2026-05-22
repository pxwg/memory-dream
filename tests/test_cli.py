from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MemoryDreamCliTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        merged_env["PYTHONPATH"] = str(ROOT / "src")
        if env:
            merged_env.update(env)
        return subprocess.run(
            [sys.executable, "-m", "memory_dream", *args],
            cwd=cwd,
            env=merged_env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_init_where_build_show_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            (project / ".git").mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("--dream-root", str(dream_root), "init", cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertFalse((project / "Memory.md").exists())
            self.assertTrue((dream_root / "dream.toml").exists())

            source = next((dream_root / "projects").iterdir()) / "source"
            note = source / "note" / "2605221059.typ"
            note.write_text(
                "\n".join(
                    [
                        '#import "../include.typ": *',
                        "#let zk-metadata = toml(bytes(",
                        "  ```toml",
                        "  schema-version = 1",
                        '  relation = "active"',
                        "  ``` .text,",
                        "))",
                        "#show: zettel.with(metadata: zk-metadata)",
                        "",
                        "= Memory Dream <2605221059>",
                        "#tag.idea",
                        "See @2605221059",
                    ]
                ),
                encoding="utf-8",
            )
            related = source / "note" / "2605221100.typ"
            related.write_text(
                "\n".join(
                    [
                        '#import "../include.typ": *',
                        "",
                        "= Related Note <2605221100>",
                        "Back to @2605221059",
                    ]
                ),
                encoding="utf-8",
            )
            (source / "index.typ").write_text(
                "\n".join(
                    [
                        '#import "include.typ": *',
                        "= Project Memory",
                        "",
                        "- @2605221059",
                    ]
                ),
                encoding="utf-8",
            )

            subdir = project / "subdir"
            subdir.mkdir()
            where = self.run_cli("--dream-root", str(dream_root), "where", cwd=subdir, env=env)
            self.assertEqual(where.returncode, 0, where.stderr)
            self.assertIn("source:", where.stdout)

            build = self.run_cli("--dream-root", str(dream_root), "build", cwd=subdir, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)
            artifact = next((dream_root / "projects").iterdir()) / "artifact"
            memory = artifact / "Memory.md"
            card = artifact / "memory" / "2605221059-memory-dream.md"
            related_card = artifact / "memory" / "2605221100-related-note.md"
            self.assertTrue(memory.exists())
            self.assertTrue(card.exists())
            self.assertTrue(related_card.exists())
            self.assertIn("[Memory Dream @2605221059](memory/2605221059-memory-dream.md)", memory.read_text())
            self.assertIn("tags = [\"idea\"]", card.read_text())
            self.assertIn("[Memory Dream @2605221059](2605221059-memory-dream.md)", related_card.read_text())

            show = self.run_cli("--dream-root", str(dream_root), "show", cwd=project, env=env)
            self.assertEqual(show.returncode, 0, show.stderr)
            self.assertIn("# Project Memory", show.stdout)

            check = self.run_cli("--dream-root", str(dream_root), "check", cwd=project, env=env)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_unregistered_project_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            result = self.run_cli("--dream-root", str(base / "dream"), "where", cwd=project)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unregistered project", result.stderr)

    def test_check_preserves_zk_lsp_exit_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            source = dream_root / "projects" / "project-123456" / "source"
            artifact = dream_root / "projects" / "project-123456" / "artifact"
            cache = dream_root / "projects" / "project-123456" / "cache"
            (source / "note").mkdir(parents=True)
            artifact.mkdir(parents=True)
            cache.mkdir(parents=True)
            (source / "index.typ").write_text("= Project Memory\n", encoding="utf-8")
            (dream_root / "dream.toml").write_text(
                "\n".join(
                    [
                        "version = 1",
                        "",
                        "[[project]]",
                        'id = "project-123456"',
                        'name = "project"',
                        f'root = "{project}"',
                        f'source = "{source}"',
                        f'artifact = "{artifact}"',
                        f'cache = "{cache}"',
                        'created_at = "2026-05-22T00:00:00+08:00"',
                        'updated_at = "2026-05-22T00:00:00+08:00"',
                    ]
                ),
                encoding="utf-8",
            )
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp", check_exit=7)
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            result = self.run_cli("--dream-root", str(dream_root), "check", cwd=project, env=env)
            self.assertEqual(result.returncode, 7)

    def test_init_from_non_git_subdirectory_reuses_registered_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            subdir = project / "nested"
            subdir.mkdir(parents=True)
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            first = self.run_cli("--dream-root", str(dream_root), "init", cwd=project, env=env)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = self.run_cli("--dream-root", str(dream_root), "init", cwd=subdir, env=env)
            self.assertEqual(second.returncode, 0, second.stderr)

            registry = (dream_root / "dream.toml").read_text(encoding="utf-8")
            self.assertEqual(registry.count("[[project]]"), 1)
            self.assertIn('name = "project"', registry)
            self.assertNotIn('name = "nested"', registry)


def install_fake_zk_lsp(path: Path, *, check_exit: int = 0) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import pathlib
import sys

args = sys.argv[1:]
if args == ["init"]:
    root = pathlib.Path.cwd()
    (root / "note").mkdir(exist_ok=True)
    (root / "include.typ").write_text("", encoding="utf-8")
    (root / "index.typ").write_text("= Project Memory\\n", encoding="utf-8")
    (root / "link.typ").write_text("", encoding="utf-8")
    raise SystemExit(0)
if len(args) >= 3 and args[0] == "--wiki-root":
    command = args[2]
    if command == "generate":
        pathlib.Path(args[1], "link.typ").write_text("", encoding="utf-8")
        raise SystemExit(0)
    if command == "check":
        raise SystemExit(CHECK_EXIT)
raise SystemExit(2)
""".replace("CHECK_EXIT", str(check_exit)),
        encoding="utf-8",
    )
    path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
