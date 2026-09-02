# Literature Search

This repository pairs the `literature-search` skill with its importable `scholar` Python package.

| Path | Purpose |
| --- | --- |
| [Skill overview](SKILL.md) | Entry point and progressive-disclosure guide |
| [Instruction set](instructions/) | Task-specific operating instructions, loaded only as needed |
| [Scholar package](scripts/scholar/) | Multi-source discovery, analysis, full-text, and Zotero package |
| [References](references/) | Deeper source notes and composition diagrams |
| [Package configuration](scripts/pyproject.toml) | Dependencies and build configuration |

Run the package from `scripts/`:

```bash
cd scripts
uv run python -c "import scholar; print(scholar.search('quantum chemistry', limit=1))"
```

The skill is self-contained: install or copy this repository as the `literature-search` skill, and use the package from its `scripts/` project.
