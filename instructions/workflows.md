# Workflows and reporting

## Library context when relevant

When the task concerns the user's existing papers, collections, duplicate avoidance, or a durable save, consult the user's Zotero library early:

- Use `zotero_items(query=...)` for a focused quicksearch.
- Use `zotero_items()` for the full compact inventory.
- Use `zotero_collections(query=...)` and then `zotero_items(collection=..., subcollections=True)` when the user means a curated shelf.

Reuse existing records and DOIs. Tell the user what was already present versus what is new. For an independent external search, this lookup is optional.

## Optional discovery and analysis

Use whichever of `search`, `citations`, `similar`, `facets`, `find_authors`, `coauthors`, `author_works`, and `author_profile` answers the question. They can be composed in any order, and a task may need only one of them. Read the [analysis guidance](analysis.md) before making claims about themes or collaboration.

Keep the default search broad: do not apply type, open-access, or year filters unless the user asks. Narrowing can exclude relevant preprints, reviews, conference papers, or journal articles. If a filter is necessary, enable logging and report it.

## Full text and durable saves

Use `fulltext(paper_id, download=True)` when a paper needs to be read or saved. Use `figures(...)` for standalone embedded raster figures, but read the complete PDF when figures, equations, or tables need context. Use `zotero_save(...)` when the user wants to keep papers; read the [Zotero guidance](zotero.md) before any write.

## Warnings and failures

Never hide incomplete work. Surface:

- Logged warnings for narrowing filters, per-source caps, source failures, and fallbacks.
- Batch `_error` entries and `meta.failed` counts.
- Zotero `skipped`, `errors`, `create_failures`, attachment failures, and `has_pdf: false`.
- A missing abstract, missing topic data, unavailable full text, or a source that was not consulted.

Logging is automatic. Read stderr and the temporary scanlit log before reporting the result.

## Verification and comprehension

Treat every retrieved fact, stored note, prior result, and remembered detail as a lead to verify against the live source. Retrieval is not comprehension: read the abstract, topic tags, citation contexts, warnings, failure fields, and actual PDF pages that you fetch. If a field is not read or used, say why it was set aside.

Use the strongest available source for each claim. Cite title, authors, year, venue, identifier, citation count, DOI or URL, and open-access status. Say when a conclusion rests on an abstract rather than the full text.

## Example composition, not a requirement

One possible combination, when the task needs all of these activities, is:

1. Zotero inventory.
2. Live discovery and analysis.
3. Open-access routing and PDF reading for the few papers that matter.
4. Complete Zotero save, including the PDF whenever one could be retrieved.
5. Report new items, skipped items, exclusions, failures, and unresolved uncertainty.

Reorder, omit, or repeat any step when the question calls for it.
