--- name: literature-search title: Find, analyze, read scholarly papers and save them to Zotero enabled: true description: >- Scholarly-literature instructions: a per-task folder of Markdown files (`tasks/`) describing how to find papers, analyze citations and authors, obtain open-access full text, inspect figures, and manage the Zotero library and Obsidian notes, using the raw APIs of OpenAlex, Crossref, Semantic Scholar, arXiv, PubMed, Europe PMC, Unpaywall, and Zotero. ---

# Literature Search

Follow **`tasks/00-overview.md`**, then open the single task file it points to for the job at hand. Those files are self-contained: each gives the endpoints, the parameters that matter, and the traps, and they are meant to be worked directly with `curl`/`jq` or a short script.

> **These instructions supersede the `scanlit` Python package.** Do not install or import `scanlit`.
> The package under `scripts/scanlit/` is kept only as historical reference and is no longer the
> interface; `tasks/` is.

## Task files

- `tasks/00-overview.md` — conventions, credentials, and the index.
- `tasks/search.md` — discovery across databases.
- `tasks/paper-metadata.md` — one paper from an id.
- `tasks/citations.md` — forward/backward citation traversal.
- `tasks/similar-papers.md` — related work.
- `tasks/facets.md` — corpus counts.
- `tasks/authors.md` — disambiguation, co-authors, an author's works.
- `tasks/fulltext.md` — find and download a PDF.
- `tasks/figures.md` — figure images from a PDF.
- `tasks/webpage-snapshot.md` — archive a URL.
- `tasks/zotero.md` — the library (read, save, attach, update, delete).
- `tasks/obsidian-notes.md` — the vault note for a paper.

The older `instructions/`, `references/`, and `README.md` describe the retired package; prefer `tasks/`.
