# Reading and full-text acquisition

## Open-access routing

`fulltext(paper_id)` reports discovered open-access locations. With `download=True`, `source="auto"` tries Sci-Hub mirrors (including `.jp`) **first**, then every discovered open-access PDF URL, then Anna’s member and slow routes. It saves only validated, readable PDFs to `out_path`, `out_dir`, or a temporary directory. `source="scihub"`, `"open_access"`, `"annas_archive"`, or `"annas_archive_slow"` attempts that source alone (no silent fallback). Metadata and `routes` are still returned even if no PDF is found. Open-access location discovery includes:

- arXiv PDF for an arXiv identifier;
- Europe PMC / PMC full-text XML for a PMCID;
- the open-access copy recorded by OpenAlex;
- Unpaywall for DOI-based open-access locations;
- bioRxiv or medRxiv JATS XML for a `10.1101/...` DOI;
- CORE repository full text;
- optional fallback routes described in the [source notes](../references/sources.md) when configured.

A DOI lookup through Unpaywall requires an email parameter. OpenAlex may return an inverted abstract index; the package reconstructs the readable abstract in the normalized record.

An HTML page with a `.pdf` filename or `application/pdf` content type is **not** a PDF. PDF files are checked for a `%PDF-` header and parsed for at least one readable page. If no valid PDF is found, `pdf_path` remains `None`; report the failure and reason only from the abstract. Do not fabricate text, figures, equations, or results.

## Validate local files before Zotero

`pdf_check("/path/to/file.pdf")` returns `valid`, `pages`, `bytes`, and `error` without saving or uploading. `zotero_attach(...)` refuses invalid PDFs before creating any remote child. A `zotero_save` may still create article metadata without a valid PDF: inspect `pdf_errors` and `meta.pdf_failures`; `has_pdf: false` is not a successful attachment. For a specific fallback, call `fulltext(doi, download=True, source="annas_archive")` explicitly, inspect its return, then attach the verified file to an existing Zotero item.

## Reading files

Read the PDF itself so figures, equations, tables, and surrounding claims remain in context. Use `figures(...)` only when standalone embedded raster images are useful; it can miss vector or composed figures. A retrieved file is not automatically understood: inspect it before reporting.

`webpage_snapshot(url, out_path=...)` saves a full-page webpage artifact as PDF, with an HTML fallback if the browser is unavailable. `book_fulltext(isbn, download=True)` is a separate book route and returns a PDF path when configured and successful.

## Optional Anna's Archive configuration

The optional Anna's Archive member route needs `ANNAS_SECRET_KEY` and an active paid membership. The keyless slow route needs a running FlareSolverr instance referenced by `FLARESOLVERR_URL`; it can take minutes per paper. Check the [source notes](../references/sources.md) for exact behavior and report when either route was unavailable.

## Figures and local state

`figures(...)` returns a `workdir` and image paths. Read the generated images. A local PDF path proves local availability; a remote URL or remote attachment hash does not. Keep local and remote attachment state distinct when the file is later saved to Zotero.
