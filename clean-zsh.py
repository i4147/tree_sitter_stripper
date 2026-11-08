#!/data/data/com.termux/files/usr/bin/env python
from multiprocessing import Pool
from pathlib import Path
import sys

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from tree_sitter import Language, Node, Parser
import tree_sitter_zsh


_PARSER: Parser | None = None


def get_parser() -> Parser:
    global _PARSER
    if _PARSER is None:
        lang = Language(tree_sitter_zsh.language())
        try:
            _PARSER = Parser(lang)
        except TypeError:
            _PARSER = Parser()
            _PARSER.set_language(lang)
    return _PARSER


def is_zsh_file(path: Path) -> bool:
    if path.suffix == ".zsh":
        return True
    if path.suffix == "":
        try:
            with path.open("rb") as fh:
                head = fh.readline(200)
        except OSError:
            return False
        return head.startswith(b"#!") and b"zsh" in head
    return False


def find_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and is_zsh_file(p)]


def _collect_comments(node: Node, ranges: list[tuple[int, int]]) -> None:
    if node.type == "comment":
        ranges.append((node.start_byte, node.end_byte))
        return
    for child in node.children:
        _collect_comments(child, ranges)


def _strip_ranges(source: bytes, ranges: list[tuple[int, int]]) -> bytes:
    if source.startswith(b"#!"):
        ranges = [r for r in ranges if r[0] != 0]
    if not ranges:
        return source
    ranges = sorted(ranges)
    merged: list[tuple[int, int]] = [ranges[0]]
    for start, end in ranges[1:]:
        ls, le = merged[-1]
        if start <= le:
            merged[-1] = (ls, max(le, end))
        else:
            merged.append((start, end))
    out = bytearray()
    pos = 0
    for start, end in merged:
        out.extend(source[pos:start])
        pos = end
    out.extend(source[pos:])
    return bytes(out)


def _remove_blank_lines(source: bytes) -> bytes:
    return b"".join(line for line in source.splitlines(keepends=True) if line.strip())


def _has_error(node: Node) -> bool:
    if node.type == "ERROR" or node.is_missing:
        return True
    return any(_has_error(c) for c in node.children)


def _validate(result: bytes) -> bool:
    try:
        tree = get_parser().parse(result)
    except Exception:
        return False
    return not _has_error(tree.root_node)


def process_file(path: Path) -> tuple[Path, int, int, str]:
    try:
        source = path.read_bytes()
    except OSError:
        return path, 0, 0, "read_error"
    tree = get_parser().parse(source)
    ranges: list[tuple[int, int]] = []
    _collect_comments(tree.root_node, ranges)
    stripped = _remove_blank_lines(_strip_ranges(source, ranges))
    if not _validate(stripped):
        return path, len(source), 0, "invalid"
    reduced = len(source) - len(stripped)
    if reduced > 0:
        try:
            path.write_bytes(stripped)
        except OSError:
            return path, len(source), 0, "write_error"
    return path, len(source), reduced, "unchanged" if reduced == 0 else "ok"


def _render(results: list[tuple[int, tuple[Path, int, int, str]]], total: int) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    idx_w = len(f"[{total}/{total}]")
    table.add_column("idx", justify="right", no_wrap=True, width=idx_w)
    table.add_column("fname", overflow="ellipsis", no_wrap=True)
    table.add_column("bytes", justify="right", no_wrap=True, width=10)
    for i, (path, _orig, reduced, _status) in results:
        style = "green" if reduced > 0 else "dim"
        table.add_row(f"[{i}/{total}]", path.name, Text(str(reduced), style=style))
    return table


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else Path.cwd()
    files = find_files(root)
    total = len(files)
    console = Console()
    if total == 0:
        console.print("[yellow]No .zsh files found[/]")
        return 0
    results: list[tuple[int, tuple[Path, int, int, str]]] = []
    total_freed = 0
    with Live(console=console, refresh_per_second=15, transient=False) as live:
        live.update(_render(results, total))
        with Pool(processes=4) as pool:
            for i, res in enumerate(pool.imap_unordered(process_file, files), 1):
                results.append((i, res))
                total_freed += res[2]
                live.update(_render(results, total))
    console.print(f"\n[bold]Total freed:[/] [green]{total_freed}[/] bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
