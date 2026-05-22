from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
import hashlib
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

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertFalse((project / "Memory.md").exists())
            self.assertTrue((dream_root / "dream.toml").exists())

            source = (next((dream_root / "projects").iterdir()) / "source").resolve()
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
            where = self.run_cli("where", "--dream-root", str(dream_root), cwd=subdir, env=env)
            self.assertEqual(where.returncode, 0, where.stderr)
            self.assertIn("source:", where.stdout)

            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=subdir, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)
            artifact = (next((dream_root / "projects").iterdir()) / "artifact").resolve()
            memory = artifact / "Memory.md"
            card = artifact / "memory" / "2605221059-memory-dream.md"
            related_card = artifact / "memory" / "2605221100-related-note.md"
            self.assertTrue(memory.exists())
            self.assertTrue(card.exists())
            self.assertTrue(related_card.exists())
            self.assertIn("[Memory Dream @2605221059](memory/2605221059-memory-dream.md)", memory.read_text())
            self.assertIn("tags = [\"idea\"]", card.read_text())
            self.assertNotIn("))", card.read_text())
            self.assertIn("[Memory Dream @2605221059](2605221059-memory-dream.md)", related_card.read_text())

            show = self.run_cli("show", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(show.returncode, 0, show.stderr)
            self.assertIn("# Project Memory", show.stdout)

            context = self.run_cli("context", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(context.returncode, 0, context.stderr)
            self.assertIn("# Project Memory Context", context.stdout)
            self.assertIn(f"- artifact-root: `{artifact}`", context.stdout)
            self.assertIn("## Memory.md", context.stdout)
            self.assertIn("## Referenced Notes", context.stdout)
            self.assertIn("### 2605221059-memory-dream.md", context.stdout)
            self.assertIn(f"- artifact: `{card}`", context.stdout)
            self.assertIn(f"- source-candidate: `{source / 'note' / '2605221059.typ'}`", context.stdout)
            self.assertNotIn("### 2605221100-related-note.md", context.stdout)

            check = self.run_cli("check", "--dream-root", str(dream_root), cwd=project, env=env)
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

    def test_nested_git_repo_does_not_fall_back_to_parent_registration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            parent = base / "parent"
            nested = parent / "nested"
            nested.mkdir(parents=True)
            (parent / ".git").mkdir()
            (nested / ".git").mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            parent_init = self.run_cli("--dream-root", str(dream_root), "init", cwd=parent, env=env)
            self.assertEqual(parent_init.returncode, 0, parent_init.stderr)

            nested_where = self.run_cli("--dream-root", str(dream_root), "where", cwd=nested, env=env)
            self.assertEqual(nested_where.returncode, 1)
            self.assertIn("unregistered project", nested_where.stderr)

            nested_init = self.run_cli("--dream-root", str(dream_root), "init", cwd=nested, env=env)
            self.assertEqual(nested_init.returncode, 0, nested_init.stderr)
            registry = (dream_root / "dream.toml").read_text(encoding="utf-8")
            self.assertEqual(registry.count("[[project]]"), 2)
            self.assertIn('name = "parent"', registry)
            self.assertIn('name = "nested"', registry)

    def test_build_rejects_unmanaged_artifact_path_without_deleting_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            source = dream_root / "projects" / "project-123456" / "source"
            cache = dream_root / "projects" / "project-123456" / "cache"
            unsafe_artifact = base / "unsafe-artifact"
            (source / "note").mkdir(parents=True)
            cache.mkdir(parents=True)
            unsafe_artifact.mkdir()
            sentinel = unsafe_artifact / "do-not-delete.txt"
            sentinel.write_text("keep", encoding="utf-8")
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
                        f'artifact = "{unsafe_artifact}"',
                        f'cache = "{cache}"',
                        'created_at = "2026-05-22T00:00:00+08:00"',
                        'updated_at = "2026-05-22T00:00:00+08:00"',
                    ]
                ),
                encoding="utf-8",
            )
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            result = self.run_cli("--dream-root", str(dream_root), "build", cwd=project, env=env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid registry", result.stderr)
            self.assertTrue(sentinel.exists())

    def test_build_rejects_filename_header_mismatch_before_cleaning_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            artifact = project_dir / "artifact"
            sentinel = artifact / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            (source / "note" / "2605221059.typ").write_text("= First <2605221059>\n", encoding="utf-8")
            (source / "note" / "2605221100.typ").write_text("= Second <2605221059>\n", encoding="utf-8")

            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 1)
            self.assertIn("note filename does not match header id", build.stderr)
            self.assertTrue(sentinel.exists())

    def test_registry_id_escape_is_rejected_without_deleting_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            escaped_base = base / "escape"
            source = escaped_base / "source"
            artifact = escaped_base / "artifact"
            cache = escaped_base / "cache"
            (source / "note").mkdir(parents=True)
            artifact.mkdir(parents=True)
            cache.mkdir(parents=True)
            sentinel = artifact / "do-not-delete.txt"
            sentinel.write_text("keep", encoding="utf-8")
            (source / "index.typ").write_text("= Project Memory\n", encoding="utf-8")
            dream_root.mkdir()
            (dream_root / "dream.toml").write_text(
                "\n".join(
                    [
                        "version = 1",
                        "",
                        "[[project]]",
                        'id = "../../escape"',
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
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            result = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid project id", result.stderr)
            self.assertTrue(sentinel.exists())

    def test_failed_init_cleans_unregistered_project_dir_for_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            fake = bin_dir / "zk-lsp"
            install_fake_zk_lsp(fake, init_exit=2, write_partial=True)
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            failed = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(failed.returncode, 1)
            self.assertFalse(any((dream_root / "projects").glob("*")))

            install_fake_zk_lsp(fake)
            retried = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(retried.returncode, 0, retried.stderr)
            self.assertTrue((dream_root / "dream.toml").exists())

    def test_frontmatter_reserved_metadata_keys_are_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            note = source / "note" / "2605221059.typ"
            note.write_text(
                "\n".join(
                    [
                        '#import "../include.typ": *',
                        "#let zk-metadata = toml(bytes(",
                        "  ```toml",
                        '  "title" = "Conflicting"',
                        '  "source" = "conflicting.typ"',
                        '  "tags" = ["conflict"]',
                        '  relation = "active"',
                        "  ```",
                        "))",
                        "",
                        "= Memory Dream <2605221059>",
                    ]
                ),
                encoding="utf-8",
            )

            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)
            card = project_dir / "artifact" / "memory" / "2605221059-memory-dream.md"
            frontmatter = card.read_text(encoding="utf-8").split("+++", 2)[1]
            parsed = tomllib.loads(frontmatter)
            self.assertEqual(parsed["title"], "Memory Dream")
            self.assertEqual(parsed["source"], "note/2605221059.typ")
            self.assertEqual(parsed["relation"], "active")

    def test_init_rejects_preexisting_project_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            projects_root = dream_root / "projects"
            projects_root.mkdir(parents=True)
            project_id = f"project-{hashlib.sha1(str(project.resolve()).encode('utf-8')).hexdigest()[:6]}"
            outside = base / "outside"
            outside.mkdir()
            (projects_root / project_id).symlink_to(outside, target_is_directory=True)
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            result = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(result.returncode, 1)
            self.assertIn("not a plain directory", result.stderr)
            self.assertFalse((outside / "source").exists())

    def test_newline_project_path_round_trips_in_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project\nwith-newline"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            where = self.run_cli("where", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(where.returncode, 0, where.stderr)

    def test_build_failure_keeps_existing_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            artifact = project_dir / "artifact"
            old_memory = artifact / "Memory.md"
            old_memory.write_text("old memory", encoding="utf-8")
            (source / "note" / "2605221059.typ").write_text(
                "\n".join(
                    [
                        "#let zk-metadata = toml(bytes(",
                        "  ```toml",
                        "  broken =",
                        "  ```",
                        "))",
                        "= Broken <2605221059>",
                    ]
                ),
                encoding="utf-8",
            )

            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 1)
            self.assertEqual(old_memory.read_text(encoding="utf-8"), "old memory")

    def test_context_can_include_all_notes_or_limit_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            (source / "index.typ").write_text(
                "\n".join(
                    [
                        "= Project Memory",
                        "",
                        "- @2605221059",
                        "- @2605221100",
                    ]
                ),
                encoding="utf-8",
            )
            (source / "note" / "2605221059.typ").write_text("= First <2605221059>\n", encoding="utf-8")
            (source / "note" / "2605221100.typ").write_text("= Second <2605221100>\n", encoding="utf-8")
            (source / "note" / "2605221200.typ").write_text("= Unreferenced <2605221200>\n", encoding="utf-8")

            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)

            limited = self.run_cli("context", "--dream-root", str(dream_root), "--max-notes", "1", cwd=project, env=env)
            self.assertEqual(limited.returncode, 0, limited.stderr)
            self.assertIn("### 2605221059-first.md", limited.stdout)
            self.assertNotIn("### 2605221100-second.md", limited.stdout)
            self.assertNotIn("### 2605221200-unreferenced.md", limited.stdout)
            self.assertIn("<!-- 1 referenced note(s) omitted by --max-notes. -->", limited.stdout)

            all_notes = self.run_cli("context", "--dream-root", str(dream_root), "--all", cwd=project, env=env)
            self.assertEqual(all_notes.returncode, 0, all_notes.stderr)
            self.assertIn("## All Notes", all_notes.stdout)
            self.assertIn("### 2605221059-first.md", all_notes.stdout)
            self.assertIn("### 2605221100-second.md", all_notes.stdout)
            self.assertIn("### 2605221200-unreferenced.md", all_notes.stdout)

    def test_context_reports_missing_referenced_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            source = dream_root / "projects" / "project-123456" / "source"
            artifact = dream_root / "projects" / "project-123456" / "artifact"
            cache = dream_root / "projects" / "project-123456" / "cache"
            (source / "note").mkdir(parents=True)
            (artifact / "memory").mkdir(parents=True)
            cache.mkdir(parents=True)
            (source / "index.typ").write_text("= Project Memory\n", encoding="utf-8")
            (artifact / "Memory.md").write_text("[Missing](memory/2605221059-missing.md)\n", encoding="utf-8")
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

            context = self.run_cli("context", "--dream-root", str(dream_root), cwd=project)
            self.assertEqual(context.returncode, 1)
            self.assertIn("context references missing note artifacts", context.stderr)

    def test_context_rejects_stale_index_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            (source / "note" / "2605221059.typ").write_text("= First <2605221059>\n", encoding="utf-8")
            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)

            memory = project_dir / "artifact" / "Memory.md"
            newer = memory.stat().st_mtime + 10
            (source / "index.typ").write_text("= Project Memory\n\n- stale\n", encoding="utf-8")
            os.utime(source / "index.typ", (newer, newer))

            context = self.run_cli("context", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(context.returncode, 1)
            self.assertIn("artifact stale", context.stderr)
            self.assertIn("run `memory-dream build`", context.stderr)

    def test_context_rejects_unbuilt_new_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            bin_dir = base / "bin"
            bin_dir.mkdir()
            install_fake_zk_lsp(bin_dir / "zk-lsp")
            env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            init = self.run_cli("init", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(init.returncode, 0, init.stderr)
            project_dir = next((dream_root / "projects").iterdir())
            source = project_dir / "source"
            build = self.run_cli("build", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(build.returncode, 0, build.stderr)

            (source / "note" / "2605221059.typ").write_text("= New Note <2605221059>\n", encoding="utf-8")

            context = self.run_cli("context", "--dream-root", str(dream_root), cwd=project, env=env)
            self.assertEqual(context.returncode, 1)
            self.assertIn("artifact stale: missing", context.stderr)
            self.assertIn("run `memory-dream build`", context.stderr)

    def test_bad_registry_project_entry_reports_user_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project.mkdir()
            dream_root = base / "dream"
            dream_root.mkdir()
            (dream_root / "dream.toml").write_text("version = 1\nproject = [1]\n", encoding="utf-8")

            result = self.run_cli("where", "--dream-root", str(dream_root), cwd=project)
            self.assertEqual(result.returncode, 1)
            self.assertIn("project entries must be tables", result.stderr)

    def test_init_rejects_missing_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            missing = base / "missing"
            dream_root = base / "dream"

            result = self.run_cli("init", "--dream-root", str(dream_root), "--project-root", str(missing), cwd=base)
            self.assertEqual(result.returncode, 1)
            self.assertIn("project root does not exist", result.stderr)


def install_fake_zk_lsp(path: Path, *, check_exit: int = 0, init_exit: int = 0, write_partial: bool = False) -> None:
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
    if WRITE_PARTIAL:
        (root / "partial.typ").write_text("partial", encoding="utf-8")
    raise SystemExit(INIT_EXIT)
if len(args) >= 3 and args[0] == "--wiki-root":
    command = args[2]
    if command == "generate":
        pathlib.Path(args[1], "link.typ").write_text("", encoding="utf-8")
        raise SystemExit(0)
    if command == "check":
        raise SystemExit(CHECK_EXIT)
raise SystemExit(2)
""".replace("CHECK_EXIT", str(check_exit))
        .replace("INIT_EXIT", str(init_exit))
        .replace("WRITE_PARTIAL", "True" if write_partial else "False"),
        encoding="utf-8",
    )
    path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
