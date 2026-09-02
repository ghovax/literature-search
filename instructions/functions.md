# Functions and composition

## Calling the package

Run from the `scripts/` directory:

```bash
uv run python -c "import scholar; print(scholar.search('quantum chemistry', limit=1))"
```

Every function returns a dict. Discovery, analysis, reading, and Zotero functions are batch-first: pass one query, paper id, or author for one result, or pass a list to fan out concurrently and receive results in input order under `results`. Zotero functions are also batch-first; writes use chunks of 50 and PDF uploads run in parallel.

Call `scholar.configure_logging()` when warnings matter. Without it, the package remains quiet; with it, narrowing filters, source failures, fallbacks, and incomplete results are visible in stderr and the diagnostic log.

## Function reference

| Function | Role | Purpose |
| --- | --- | --- |
| `search(query, ...)` | find | Search all selected sources, de-duplicate, and rank topical results. |
| `lookup(paper_id)` | analyze | Fetch one paper by DOI, arXiv id, PMID, PMCID, or OpenAlex id. |
| `citations(paper_id, direction=..., source=...)` | analyze | Traverse citing papers or references; Semantic Scholar adds influential flags and citation contexts. |
| `similar(paper_id, source=...)` | analyze | Fetch OpenAlex related works or Semantic Scholar recommendations. |
| `facets(query, by=...)` | analyze | Count works by year, institution, venue, type, open-access status, topic, or country. |
| `find_authors(name)` | analyze | Return candidate OpenAlex authors for disambiguation. |
| `coauthors(author)` | analyze | Return an author's most frequent collaborators with metrics. |
| `author_works(author, coauthor=..., maximum_results=...)` | analyze | Return an author's works, or only the joint works with a coauthor. |
| `author_profile(author)` | analyze | Return topics, concepts, metrics, name variants, and affiliation history. |
| `fulltext(paper_id, download=...)` | read | Find full-text routes and optionally save the best PDF. |
| `figures(paper_id=...)` | read | Extract embedded raster figures from a PDF. |
| `book_fulltext(isbn, download=...)` | read | Acquire a book PDF by ISBN when the configured book route is available. |
| `webpage_snapshot(url, out_path=...)` | read | Save a webpage as a full-page PDF or HTML fallback. |
| `zotero_save(papers, ...)` | zotero | Deduplicate, enrich, create Zotero items, and attach PDFs. |
| `zotero_create(items)` | zotero | Create editable Zotero item JSON in batches. |
| `zotero_update(updates)` | zotero | PATCH existing Zotero items; only supplied fields change. |
| `zotero_delete(keys)` | zotero | Delete Zotero items by key. |
| `zotero_attach(attachments)` | zotero | Upload PDFs as child attachments. |
| `zotero_items(query=..., tag=..., collection=..., subcollections=..., limit=..., full=...)` | zotero | Read the library or quicksearch it, optionally within a collection. |
| `zotero_collections(query=...)` | zotero | Find collections and their keys and paths. |
| `zotero_get(keys, children=...)` | zotero | Fetch complete item JSON and, optionally, child notes and attachments. |
| `obsidian_create(zotero_key)` | obsidian | Create an Obsidian note from a Zotero item if it does not exist. |
| `obsidian_read(zotero_key)` | obsidian | Read the user's Obsidian comments for a Zotero item. |
| `configure_logging()` | — | Enable diagnostic warnings and the flushed temporary run log. |

## Interface contract

- Scalar input returns one operation result; list input returns a batch result in input order.
- Every result has `meta`. List-producing calls use `results`; scalar lookups use `result`.
- Batched calls report `meta.ok` and `meta.failed`; a failed input appears in place as `{"_error": "...", "input": ...}`.
- Zotero writes report per-item success or failure directly. `zotero_save` additionally reports `created`, `skipped`, `attachments`, `create_failures`, `errors`, and `library_version`.
- Each scholarly record carries an `ids` object (`doi`, `arxiv`, `pmid`, `pmcid`, `openalex`, and sometimes `s2`). Pass those ids directly into subsequent calls.

## Credentials

Credentials come from the environment or a project `.env`:

- `S2_API_KEY` for reliable Semantic Scholar access.
- `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, and `ZOTERO_LIBRARY_TYPE` for Zotero.
- `CORE_API_KEY` for a higher CORE rate limit.
- `ANNAS_SECRET_KEY` and `FLARESOLVERR_URL` only for the optional last-resort full-text routes described in the [reading guidance](reading.md) and [source notes](../references/sources.md).

Never hardcode credentials or print them in output.
