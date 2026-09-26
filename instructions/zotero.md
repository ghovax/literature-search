# Zotero and durable saves

## Complete saves

Use `zotero_save(...)` for a list of papers. Pass `pdf_source="scihub"`, `"open_access"`, `"annas_archive"`, or `"annas_archive_slow"` to restrict acquisition to that route; `"auto"` tries Sci-Hub (including `.jp`), then open-access, then Anna. It resolves identifiers, deduplicates by DOI against the live library, fetches bibliographic metadata, downloads the best available PDF, creates items in batches, and uploads child attachments in parallel.

A saved paper is complete only when it has:

- title;
- every author;
- journal or other container;
- year/date, volume, issue, and pages when available;
- DOI, ISSN, URL, and language when available;
- a clean abstract;
- the attached PDF whenever one could be retrieved.

Closed-access papers may still be saved as complete metadata with `has_pdf: false`; say so. HTML or broken PDF downloads are rejected; inspect `pdf_errors` and `meta.pdf_failures`. `created[].has_pdf` is true only after the file upload succeeds. Do not add tags unless the user asks for them. Deduplication is on by default; use `dedup=False` only when the user explicitly wants a duplicate.

## Metadata enrichment

Use DOI-based Crossref metadata and OpenAlex abstracts/fields to fill empty fields. Fill only missing fields; never overwrite good data. Read and clean an abstract by hand when formatting is wrong. Preserve wording, remove markup and stray leading “Abstract”, and use UTF-8 Unicode for formulas and symbols such as `H₂`, `C₃N₄`, `10⁸`, `≤`, `≈`, and `Δ`. Do not put LaTeX in Zotero fields.

If an abstract is truncated or missing, follow the DOI to the publisher and retrieve the complete abstract when possible. If no abstract exists anywhere, record that fact rather than inventing one.

## Attachment state

A successful `zotero_attach` result and a child attachment `md5` from `zotero_get(..., children=True)` prove that the *validated file bytes* are registered in the remote Zotero library, not that Zotero Desktop has downloaded it into its local `storage/` cache. When investigating older attachments, inspect actual bytes: legacy saves could register HTML under a PDF filename. Report these states separately as `remote_uploaded` and `locally_cached`.

When the user mentions a gray PDF icon or asks whether a file is local, check the exact local Zotero storage path. Do not infer local availability from a remote hash, and do not infer remote upload success from a local file alone.

Write results are directly verifiable from the returned keys and per-item statuses; no read-back is needed for the write operation itself. A separate `zotero_get(..., children=True)` plus a local filesystem check is still required when attachment caching or desktop availability matters.

## Low-level operations

Use `pdf_check(path)` to inspect local PDFs without a network call. `zotero_attach` validates every supplied file *before* creating any attachment child. Use `zotero_items()` to inspect and build a dedup set; `zotero_create`, `zotero_update`, `zotero_delete`, and `zotero_attach` for fine-grained batched control. `zotero_update` has PATCH semantics. Zotero item JSON uses fields such as `itemType`, `publicationTitle`, `creators`, `DOI`, `ISSN`, `abstractNote`, `tags`, and `collections`.

All package operations use the Zotero Web API at `api.zotero.org`, including reads. Zotero's local API at `http://localhost:23119/api/` is faster and unauthenticated but is read-only in the supported workflow; using one Web API transport keeps reads and writes consistent.

## Backups

Back up from the Zotero desktop client: File → Export Library → Zotero RDF, with files and notes included. Restore through the desktop client. The Zotero Web API used here cannot import RDF, and the live Zotero data directory should not be tracked in git.

## Obsidian notes

`obsidian_create(zotero_key)` resolves article and attachment keys to parent metadata and creates `vault/<DOI prefix>/<DOI suffix>.md`: every `/` in the DOI is an actual directory, not a character replaced in a filename. DOI-less books go directly under `vault/Books/<canonical ISBN>.md` (verify ISBN-10/13 checksum; remove display hyphens/spaces; do not fall back to title or Zotero key); there is no key-named legacy lookup. Every existing file, including a zero-byte placeholder, is left unchanged. New notes are created exclusively (`x` mode) to prevent a race from overwriting a concurrently created file. The Markdown body is loaded from the packaged `scripts/scanlit/templates/paper.md` and substitutes `{{ title }}` and `{{ abstract }}` once; Zotero-derived YAML front matter is safely serialized separately. The Zotero key remains in front matter for verification. `obsidian_read(zotero_key)` resolves and reads the new path. These comments are distinct from PDF annotations: fetch annotations through `zotero_get(..., children=True)` and read the PDF separately.
