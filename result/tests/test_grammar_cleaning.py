"""Integration coverage across the available repository tree-sitter grammars."""

from pathlib import Path

import pytest

from result import tree_sitter_strip as stripper


GRAMMAR_SAMPLES: tuple[tuple[str, bytes], ...] = (
    ("bash", b"echo value # comment\n"),
    ("c", b"int value; // comment\n"),
    ("cpp", b"int value; // comment\n"),
    ("css", b"a { color: red; /* comment */ }\n"),
    ("html", b"<!-- comment --><p>value</p>\n"),
    ("javascript", b"let value = 1; // comment\n"),
    ("lua", b"-- comment\nprint('value')\n"),
    ("rust", b"fn main() {} // comment\n"),
    ("toml", b"value = 1 # comment\n"),
    ("typescript", b"let value: number = 1; // comment\n"),
    ("tsx", b"const value = <p />; // comment\n"),
    ("zsh", b"echo value # comment\n"),
)


@pytest.mark.parametrize(("language", "source"), GRAMMAR_SAMPLES)
def test_available_grammars_remove_comments_and_validate(language: str, source: bytes, tmp_path: Path) -> None:
    extension = {
        "bash": ".sh",
        "c": ".c",
        "cpp": ".cpp",
        "css": ".css",
        "html": ".html",
        "javascript": ".js",
        "lua": ".lua",
        "rust": ".rs",
        "toml": ".toml",
        "typescript": ".ts",
        "tsx": ".tsx",
        "zsh": ".zsh",
    }[language]
    path = tmp_path / f"source{extension}"
    path.write_bytes(source)
    result = stripper.process_file(path)
    assert result.status == "changed"
    cleaned = path.read_bytes()
    assert b"comment" not in cleaned
    assert stripper.is_valid(stripper.get_parser(language), cleaned)
