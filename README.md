# Literature Search

This repository pairs the `literature-search` skill with its importable `scanlit` Python package.

| Path                                       | Purpose                                                         |
| ------------------------------------------ | --------------------------------------------------------------- |
| [Skill overview](SKILL.md)                 | Entry point and progressive-disclosure guide                    |
| [Instruction set](instructions/)           | Task-specific operating instructions, loaded only as needed     |
| [Scanlit source package](scripts/scanlit/) | Multi-source discovery, analysis, full-text, and Zotero package |
| [References](references/)                  | Deeper source notes and composition diagrams                    |
| [Package configuration](pyproject.toml)    | Dependencies, build configuration, and PyPI metadata            |

Run it from this repository's root.

Install the published distribution into another project with `uv`. The package is distributed as `scanlit` and imported as `scanlit`.

The skill is self-contained: install or copy this repository as the `literature-search` skill, while the Python package can be installed independently.

## PDF integrity and precise sources

PDF acquisition and validation live together in `scripts/scanlit/pdf.py`.

`scanlit.pdf_check(path)` validates a local PDF without uploading it. `scanlit.fulltext(doi, download=True, source="scihub")` downloads from a single selected source; `source="auto"` tries Sci-Hub (including `.jp`), open-access URLs, then configured Anna routes. `scanlit.zotero_save(doi, collections=[key], pdf_source="auto")` uploads only validated PDFs and reports `pdf_errors` when none are available. `zotero_attach` rejects HTML masquerading as a PDF before it creates any child. See [reading guidance](instructions/reading.md) and [functions](instructions/functions.md). Keep regression tests outside the repository (for example in a system temporary directory); run them with `PYTHONPATH=scripts python -m unittest discover -s /path/to/external-tests -v`.

Search responses expose per-database counts and diagnostics as `result["meta"]["sources"][name] == {"status": "ok" | "failed", "count": int, "error": str | None}`; they are not formatted status strings.

Paper notes are created under `vault/<DOI prefix>/<DOI suffix>.md` (each `/` in the DOI is a real directory). DOI-less books go under `vault/Books/<canonical ISBN>.md` (hyphens and spaces removed, checksum verified; no title/key fallback). The `zotero_key` remains only in YAML front matter. No key-named legacy paths are read or created. `obsidian_create` never writes to an existing note, even if empty. The Markdown body is loaded from `scripts/scanlit/templates/paper.md` and rendered using `{{ title }}` and `{{ abstract }}` placeholders; YAML front matter is serialized separately.
