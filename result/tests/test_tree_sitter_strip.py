"""Tests for the consolidated tree-sitter source stripper."""

from pathlib import Path

import pytest

from result import tree_sitter_strip as stripper


def test_extension_and_shebang_detection() -> None:
    assert stripper.detect_language(Path("source.ts"), b"const x = 1;") == "typescript"
    assert stripper.detect_language(Path("run"), b"#!/usr/bin/env bash\necho hi\n") == "bash"
    assert stripper.detect_language(Path("run"), b"#!/bin/zsh\necho hi\n") == "zsh"
    assert stripper.detect_language(Path("run"), b"#!/usr/bin/python\n") is None
    # An explicit supported interpreter wins over a broad file extension.
    assert stripper.detect_language(Path("run.sh"), b"#!/bin/zsh\n") == "zsh"


def test_comment_removal_keeps_tokens_separate_and_removes_blank_lines() -> None:
    source = b"const value = left/* note */right; // tail\n\n// only comment\n"
    parser = stripper.get_parser("javascript")
    tree = parser.parse(source)
    ranges = stripper.collect_comment_ranges(tree.root_node, source)
    cleaned = stripper.remove_blank_lines(stripper.remove_comment_ranges(source, ranges))
    assert b"left right;" in cleaned
    assert b"\n\n" not in cleaned
    assert b"//" not in cleaned


def test_process_file_strips_comments_preserves_shebang_and_validates(tmp_path: Path) -> None:
    shell = tmp_path / "runner"
    shell.write_bytes(b"#!/usr/bin/env bash\n# header\necho hello # inline\n\n")
    result = stripper.process_file(shell)
    assert result.status == "changed"
    assert result.reduced_bytes > 0
    assert shell.read_bytes() == b"#!/usr/bin/env bash\necho hello\n"
    assert stripper.is_valid(stripper.get_parser("bash"), shell.read_bytes())


def test_check_mode_does_not_modify_file(tmp_path: Path) -> None:
    source = b"let n = 1; // comment\n\n"
    js = tmp_path / "sample.js"
    js.write_bytes(source)
    result = stripper.process_file(js, check_only=True)
    assert result.status == "changed"
    assert result.reduced_bytes > 0
    assert js.read_bytes() == source


def test_invalid_cleaned_file_is_not_written(tmp_path: Path) -> None:
    source = b"const broken = ; // remove me\n"
    js = tmp_path / "broken.js"
    js.write_bytes(source)
    result = stripper.process_file(js)
    assert result.status == "invalid"
    assert result.reduced_bytes == 0
    assert js.read_bytes() == source


def test_discovery_filters_unsupported_and_hidden_directories(tmp_path: Path) -> None:
    (tmp_path / "main.lua").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("plain text\n", encoding="utf-8")
    hidden = tmp_path / ".git"
    hidden.mkdir()
    (hidden / "ignored.rs").write_text("fn main() {}\n", encoding="utf-8")
    names = {path.name for path in stripper.find_files([tmp_path])}
    assert names == {"main.lua"}


@pytest.mark.parametrize(
    ("extension", "language"),
    [
        (".rs", "rust"),
        (".sh", "bash"),
        (".c", "c"),
        (".cpp", "cpp"),
        (".css", "css"),
        (".html", "html"),
        (".js", "javascript"),
        (".lua", "lua"),
        (".toml", "toml"),
        (".ts", "typescript"),
        (".tsx", "tsx"),
        (".vim", "vim"),
        (".zsh", "zsh"),
    ],
)
def test_language_map_covers_repo_grammars(extension: str, language: str) -> None:
    assert stripper.detect_language(Path(f"file{extension}"), b"") == language
