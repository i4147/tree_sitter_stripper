# task: consolidate these script as one
- the output style must follow clean-zsh.py
- result script must support identifying by shebang 
  and must auto process filetypes that tree-sitter libs supports (used in scripts in this repo (tree_sitter_toml, ...))
- report an overall space freed at the end
- result code must be fully type-annotated & dicumented
- add pytest based tests and examole usage demos
- save all produced codes in `result` folder
  save the helper scripts (bash, python, ...) thst you used during this session under arena folder in root of connected repo
- final output style:
example output:
[1/23]  fname   34
[2/23]  fname    536

adjust columns with terminal width
3rd column is bytes reduced from file content print it in dim -> if = 0, default -> print in green
use rich library for printing output

- report the stats when done and commit the changes
