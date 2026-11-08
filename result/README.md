# Consolidated tree-sitter stripper

`tree_sitter_strip.py` replaces the collection of language-specific cleaners
with one in-place command. It uses the tree-sitter grammars already referenced
by this repository: Bash, C, C++, CSS, HTML, JavaScript, Lua, Rust, TOML,
TypeScript/TSX, Zsh, and Vim (when the `tree_sitter_vim` binding is installed).

## Install

For Python 3.14.10 (including Termux), install the runtime dependencies:

```sh
python -m pip install -r result/requirements.txt
```

The Vim binding is optional because there is no `tree-sitter-vim` distribution
on PyPI. If your environment provides `tree_sitter_vim`, `.vim` files are
handled too. A missing grammar is reported without preventing other files from
being cleaned.

## Use

```sh
python result/tree_sitter_strip.py                 # scan the current directory
python result/tree_sitter_strip.py src/ scripts/    # recursively scan paths
python result/tree_sitter_strip.py build.sh         # process a single file
python result/tree_sitter_strip.py --check src/     # validate/report without writing
```

The tool picks a language from the file extension, or from a supported Bash or
Zsh shebang (including extensionless files). It removes parser-recognized
comments and whitespace-only lines; HTML `<script>` and `<style>` blocks are
also scanned and validated with the JavaScript and CSS grammars. The cleaned
bytes are validated before any write. The file is atomically replaced only after successful validation;
symlinks are ignored. Hidden subdirectories are skipped during discovery.

The Rich progress table follows the `clean-zsh.py` style: `[n/total]`, a
terminal-width-truncated path, and reduced bytes. Savings are dim; zero is
green. The final line reports total bytes freed. `--check` computes potential
savings but does not write files.

## Examples

Run the disposable demos without touching repository files:

```sh
python result/demos/run_examples.py
```

Or run the test suite:

```sh
python -m pip install pytest
pytest -q result/tests
```
