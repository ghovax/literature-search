# Reading and full-text acquisition

## Open-access routing

`fulltext(paper_id)` checks the configured full-text routes and returns all routes it finds. With `download=True`, it saves the best PDF to `out_path`, `out_dir`, or a temporary directory and returns an absolute `pdf_path` plus citation metadata. Possible legal/open routes include:

- arXiv PDF for an arXiv identifier;
- Europe PMC / PMC full-text XML for a PMCID;
- the open-access copy recorded by OpenAlex;
- Unpaywall for DOI-based open-access locations;
- bioRxiv or medRxiv JATS XML for a `10.1101/...` DOI;
- CORE repository full text;
- optional fallback routes described in the [source notes](../references/sources.md) when configured.

A DOI lookup through Unpaywall requires an email parameter. OpenAlex may return an inverted abstract index; the package reconstructs the readable abstract in the normalized record.

If no PDF is found, reason only from the abstract and say that full text was unavailable. Do not fabricate text, figures, equations, or results.

## Reading files

Read the PDF itself so figures, equations, tables, and surrounding claims remain in context. Use `figures(...)` only when standalone embedded raster images are useful; it can miss vector or composed figures. A retrieved file is not automatically understood: inspect it before reporting.

`webpage_snapshot(url, out_path=...)` saves a full-page webpage artifact as PDF, with an HTML fallback if the browser is unavailable. `book_fulltext(isbn, download=True)` is a separate book route and returns a PDF path when configured and successful.

## Optional Anna's Archive configuration

The optional Anna's Archive member route needs `ANNAS_SECRET_KEY` and an active paid membership. The keyless slow route needs a running FlareSolverr instance referenced by `FLARESOLVERR_URL`; it can take minutes per paper. Check the [source notes](../references/sources.md) for exact behavior and report when either route was unavailable.

## Figures and local state

`figures(...)` returns a `workdir` and image paths. Read the generated images. A local PDF path proves local availability; a remote URL or remote attachment hash does not. Keep local and remote attachment state distinct when the file is later saved to Zotero.
