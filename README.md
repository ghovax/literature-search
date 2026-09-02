# Literature Search

This repository pairs the `literature-search` skill with its importable `scanlit` Python package.

| Path | Purpose |
| --- | --- |
| [Skill overview](SKILL.md) | Entry point and progressive-disclosure guide |
| [Instruction set](instructions/) | Task-specific operating instructions, loaded only as needed |
| [Scanlit source package](scripts/scanlit/) | Multi-source discovery, analysis, full-text, and Zotero package |
| [References](references/) | Deeper source notes and composition diagrams |
| [Package configuration](pyproject.toml) | Dependencies, build configuration, and PyPI metadata |

Run it from this repository's root.

Install the published distribution into another project with `uv`. The package is distributed as `scanlit` and imported as `scanlit`.

The skill is self-contained: install or copy this repository as the `literature-search` skill, while the Python package can be installed independently.
