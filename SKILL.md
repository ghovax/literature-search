---
name: literature-search
title: Find, analyze, read scholarly papers and save them to Zotero
enabled: true
description: >-
    Scholarly-literature instructions: a per-task folder of Markdown files (`tasks/`) describing how to find papers, analyze citations and authors, obtain open-access full text, inspect figures, and manage the Zotero library and Obsidian notes, using the raw APIs of OpenAlex, Crossref, Semantic Scholar, arXiv, PubMed, Europe PMC, Unpaywall, and Zotero.
---

# Literature Search

Open the single task file below for the job at hand; each is self-contained, giving the endpoints, the parameters that matter, and the traps, and each is meant to be worked directly with a shell (`curl`, `jq`) or a short Python snippet.

## Task files

| File | Covers |
| --- | --- |
| `tasks/find.md` | discovery, metadata, citation graph, related work, corpus counts, authors |
| `tasks/read.md` | full text (PDF), figures, web-page snapshots |
| `tasks/library.md` | Zotero (read/save/attach/update/delete) and Obsidian notes |

## Conventions that apply everywhere

**Credentials** live in the environment or a project `.env` (never hard-code them, never print them):

- `S2_API_KEY` — Semantic Scholar; without it you share an anonymous pool and will hit 429s.
- `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (`user` or `group`) — Zotero Web API.
- `CORE_API_KEY` — higher CORE rate limit (full-text route only).
- `ANNAS_SECRET_KEY`, `FLARESOLVERR_URL` — only the optional Anna's Archive routes.
- `OBSIDIAN_VAULT` — vault root for notes (a DOI note lives at `<vault>/<doi-prefix>/<doi-suffix>.md`).

**Be polite.** OpenAlex and Crossref both accept a contact address and give better service when you send it (`mailto=` on OpenAlex, `mailto=` on Crossref); use the real one, not a placeholder.

**Record shape.** Normalize everything you keep to the same fields, so any step can feed any other:

```json
{"title": "...", "authors": ["..."], "year": 2022, "venue": "...", "abstract": "...", "citations": 0, "ids": {"doi": "...", "arxiv": "...", "pmid": "...", "openalex": "W..."}}
```

`ids` is the point: it is what you pass to the next call.

**Identifiers are interchangeable.** OpenAlex resolves a DOI, PMID, PMCID, or its own `W...` id; give it `https://doi.org/<doi>` or `pmid:<id>`. arXiv is the exception — resolve it through arXiv itself, because OpenAlex indexes arXiv ids unreliably.

**Say what you did.** Report which sources answered, which failed or timed out, and what you filtered out. A silent narrowing (year window, open-access only, per-source result cap) is how a literature search quietly lies to you.

**Read before concluding.** Fetch the record; do not infer fields from the query. If a source gives no abstract, record that rather than writing one.
