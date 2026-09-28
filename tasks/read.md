# Reading papers

Goal: get the full text and figures in front of you, so you read the real thing rather than a summary of it.

## Full text

Find the PDF from a legal open-access location where one exists, in this order:

- Unpaywall — the best general source: `https://api.unpaywall.org/v2/<doi>?email=<you>`, take `best_oa_location.url_for_pdf`.
- OpenAlex — the work's `oa.pdf_url` / `best_oa_location`.
- Europe PMC — resolve a PMCID (by DOI if needed), then its `fullTextXML`.
- CORE, or arXiv / bioRxiv / medRxiv for preprints.
- Sci-Hub, then Anna's Archive, as fallbacks.

`auto` falls back in that order; when a specific source is requested, use **only** that one — never silently fall back, or the caller believes they got the route they asked for. Sci-Hub mirrors rotate and are unreliable (post-2021 papers are usually absent), often with broken TLS. Anna's Archive is dormant unless `ANNAS_SECRET_KEY` is set; the slow tier needs FlareSolverr at `FLARESOLVERR_URL`; and it is the realistic route to a textbook, keyed by ISBN rather than DOI.

**Validate every file.** Publishers serve HTML error pages under a `.pdf` name, so accept a download only if it is a real, readable, unencrypted PDF with at least one page; otherwise discard it and try the next route. Report the source you actually used.

**No PDF does not mean no paper.** Closed-access work often yields only metadata and abstract — say that, rather than reporting a failure. And do not extract text to "read" a paper: download the PDF and view it, so figures and equations survive.

## Figures

To get a paper's figure images out quickly, extract the images embedded in the PDF (from a local file, a URL, or an id to resolve first). Expect two limits: many figures are vector drawings or assembled from many elements, so they are missed or come out as fragments; and embedded images are not always stored in a format that survives a naive dump. When you actually need to read a figure, view the whole PDF — the caption and surrounding text carry the meaning. This is for quick thumbnails, not evidence.

## Web pages

To archive a page for later or to attach to a reference, render it in a headless browser to PDF — that copes with JavaScript-heavy pages without per-site special cases. Fall back to a raw HTML capture only when the browser is unavailable, and say which you produced. Rendering misses login walls, infinite scroll, and consent banners, so note whatever the snapshot obviously lacks, and check the result is a real document rather than an error page.
