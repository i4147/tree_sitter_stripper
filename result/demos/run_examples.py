#!/usr/bin/env python3
"""Create disposable Bash and TOML examples and run the unified cleaner."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT: Path = Path(__file__).resolve().parents[2]
CLEANER: Path = ROOT / "result" / "tree_sitter_strip.py"


def main() -> int:
    """Run the examples in a temporary directory and return the CLI status."""
    with tempfile.TemporaryDirectory(prefix="tree-sitter-strip-demo-") as directory:
        sample_dir: Path = Path(directory)
        shell_file: Path = sample_dir / "deploy"
        shell_file.write_text(
            "#!/usr/bin/env bash\n# Remove this explanatory comment.\necho 'deploying' # and this one\n\n",
            encoding="utf-8",
        )
        config_file: Path = sample_dir / "settings.toml"
        config_file.write_text(
            "# Remove this TOML comment.\n[service]\nname = 'demo'\n\n",
            encoding="utf-8",
        )
        shell_file.chmod(0o755)
        return subprocess.call([sys.executable, str(CLEANER), str(sample_dir)])


if __name__ == "__main__":
    raise SystemExit(main())
