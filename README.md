# Literature Search

This repository pairs the `literature-search` skill with its importable `scholar` Python
package.

| Path                     | Purpose                                                         |
| ------------------------ | --------------------------------------------------------------- |
| `SKILL.md`               | Codex skill instructions and function reference                 |
| `scripts/scholar/`       | Multi-source discovery, analysis, full-text, and Zotero package |
| `scripts/pyproject.toml` | Package dependencies and build configuration                    |
| `references/`            | Source notes and composition diagrams                           |

Run the package from `scripts/`:

```bash
cd scripts
uv run python -c "import scholar; print(scholar.search('quantum chemistry', limit=1))"
```

The skill is self-contained: install or copy this repository as the `literature-search`
skill, and use the package from its `scripts/` project.
