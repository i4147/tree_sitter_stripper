"""HTML integration tests include embedded JavaScript and CSS comments."""

from pathlib import Path

from result import tree_sitter_strip as stripper


def test_html_embedded_comments_use_script_and_style_grammars(tmp_path: Path) -> None:
    html = tmp_path / "page.html"
    original = (
        b"<script>let value = 1; // js note\n</script>"
        b"<style>a { color: red; /* css note */ }</style>\n"
    )
    html.write_bytes(original)
    result = stripper.process_file(html)
    assert result.status == "changed"
    cleaned = html.read_bytes()
    assert b"js note" not in cleaned
    assert b"css note" not in cleaned
    html_parser = stripper.get_parser("html")
    assert stripper.is_valid(html_parser, cleaned)


def test_html_comment_only_script_remains_valid(tmp_path: Path) -> None:
    html = tmp_path / "empty-script.html"
    html.write_bytes(b"<script>// remove this\n</script>\n")
    result = stripper.process_file(html)
    assert result.status == "changed"
    assert html.read_bytes() == b"<script>\n</script>\n"
