# Functions and composition

## Calling the package

Import and call `scanlit` directly from the active Python environment:

```python
from scanlit import search
result = search("quantum chemistry", limit=1)
print(result)
```

When working from this repository, install the project into the active environment once if needed (for example, `uv pip install -e .`), then use normal imports. Do not generate a script string, call `python -c`, or launch a subprocess for routine `scanlit` operations.

Keep execution visible. Show inputs before a multi-paper job and display each returned result immediately. For long downloads or Zotero writes, prefer one item or a small batch per call so progress, warnings, missing PDFs, and failures are visible while the job proceeds rather than only after the entire batch finishes.

## Function reference

| Function                                                                                    | Role     | Purpose                                                                                              |
| ------------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------- |
| `search(query, ...)`                                                                        | find     | Search all selected sources, de-duplicate, and rank topical results.                                 |
| `lookup(paper_id)`                                                                          | analyze  | Fetch one paper by DOI, arXiv id, PMID, PMCID, or OpenAlex id.                                       |
| `citations(paper_id, direction=..., source=...)`                                            | analyze  | Traverse citing papers or references; Semantic Scholar adds influential flags and citation contexts. |
| `similar(paper_id, source=...)`                                                             | analyze  | Fetch OpenAlex related works or Semantic Scholar recommendations.                                    |
| `facets(query, by=...)`                                                                     | analyze  | Count works by year, institution, venue, type, open-access status, topic, or country.                |
| `find_authors(name)`                                                                        | analyze  | Return candidate OpenAlex authors for disambiguation.                                                |
| `coauthors(author)`                                                                         | analyze  | Return an author's most frequent collaborators with metrics.                                         |
| `author_works(author, coauthor=..., maximum_results=...)`                                   | analyze  | Return an author's works, or only the joint works with a coauthor.                                   |
| `author_profile(author)`                                                                    | analyze  | Return topics, concepts, metrics, name variants, and affiliation history.                            |
| `fulltext(paper_id, download=..., source="auto")`                                           | read     | Find full-text routes and optionally save the best PDF.                                              |
| `pdf_check(pdf_path)`                                                                       | read     | Check a local file’s PDF signature, parseability, and page count before upload.                      |
| `figures(paper_id=...)`                                                                     | read     | Extract embedded raster figures from a PDF.                                                          |
| `book_fulltext(isbn, download=...)`                                                         | read     | Acquire a book PDF by ISBN when the configured book route is available.                              |
| `webpage_snapshot(url, out_path=...)`                                                       | read     | Save a webpage as a full-page PDF or HTML fallback.                                                  |
| `zotero_save(papers, pdf_source="auto", ...)`                                               | zotero   | Deduplicate, enrich, create Zotero items, and attach PDFs.                                           |
| `zotero_create(items)`                                                                      | zotero   | Create editable Zotero item JSON in batches.                                                         |
| `zotero_update(updates)`                                                                    | zotero   | PATCH existing Zotero items; only supplied fields change.                                            |
| `zotero_delete(keys)`                                                                       | zotero   | Delete Zotero items by key.                                                                          |
| `zotero_attach(attachments)`                                                                | zotero   | Preflight-validate and upload PDFs as child attachments.                                             |
| `zotero_items(query=..., tag=..., collection=..., subcollections=..., limit=..., full=...)` | zotero   | Read the library or quicksearch it, optionally within a collection.                                  |
| `zotero_collections(query=...)`                                                             | zotero   | Find collections and their keys and paths.                                                           |
| `zotero_get(keys, children=...)`                                                            | zotero   | Fetch complete item JSON and, optionally, child notes and attachments.                               |
| `obsidian_create(zotero_key)`                                                               | obsidian | Exclusively create a DOI-path or ISBN-named note from a `.md` template; never change existing files. |
| `obsidian_read(zotero_key)`                                                                 | obsidian | Read the DOI/ISBN-path Obsidian note using a Zotero key.                                             |

## Interface contract

- Scalar input returns one operation result; list input returns a batch result in input order.
- `search(...)["meta"]["sources"]` maps each source to `{"status": "ok" | "failed", "count": int, "error": str | None}`. Counts are integers, never embedded in status strings; failures have `count: 0` and a diagnostic `error`. The top-level `count` is the deduplicated result count, not a source count.
- Every result has `meta`. List-producing calls use `results`; scalar lookups use `result`.
- Batched calls report `meta.ok` and `meta.failed`; a failed input appears in place as `{"_error": "...", "input": ...}`.
- Zotero writes report per-item success or failure directly. `zotero_save` reports `created`, `skipped`, `attachments`, `create_failures`, `errors`, `pdf_errors`, and `library_version`. `meta.pdf_failures` includes missing/invalid PDFs. `created[].has_pdf` is true only after a successful upload.
- PDF source selectors for `fulltext(source=...)` and `zotero_save(pdf_source=...)`: `auto`, `scihub`, `open_access`, `annas_archive`, `annas_archive_slow`. A named source never silently falls back to a different one.
- Each scholarly record carries an `ids` object (`doi`, `arxiv`, `pmid`, `pmcid`, `openalex`, and sometimes `s2`). Pass those ids directly into subsequent calls.

## Credentials

Credentials come from the environment or a project `.env`:

- `S2_API_KEY` for reliable Semantic Scholar access.
- `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, and `ZOTERO_LIBRARY_TYPE` for Zotero.
- `CORE_API_KEY` for a higher CORE rate limit.
- `ANNAS_SECRET_KEY` and `FLARESOLVERR_URL` only for the optional last-resort full-text routes described in the [reading guidance](reading.md) and [source notes](../references/sources.md).
- `OBSIDIAN_VAULT` to place generated Obsidian notes outside the current project's `vault/` directory.

Never hardcode credentials or print them in output.
