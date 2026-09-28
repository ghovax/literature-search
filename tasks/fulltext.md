# Full text: find and download a PDF

## Find open-access locations

Collect every legal OA location for a record, then try them in order:

- arXiv: `https://arxiv.org/pdf/<arxiv-id>` (if you have an arXiv id).
- Europe PMC: resolve a PMCID (by DOI via `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<doi>&format=json&pageSize=1`), then `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`.
- Unpaywall (the best general source): `https://api.unpaywall.org/v2/<doi>?email=<you>` → `best_oa_location.url_for_pdf`.
- OpenAlex's own OA link: the `oa.pdf_url` / `best_oa_location` on the work.
- CORE: `https://api.core.ac.uk/v3/search/works/?q=doi:"<doi>"&limit=1` (send `Authorization: Bearer $CORE_API_KEY` if you have one) → the `downloadUrl`.
- Preprints: `https://api.biorxiv.org/details/biorxiv/<doi>` (or `medrxiv`).

## Acquire

`source=auto` should try, in order: **Sci-Hub → open-access → Anna's Archive member → Anna's slow**. When a specific source is requested, use **only** that one — never silently fall back, or the caller will believe they got the route they asked for.

Sci-Hub mirrors rotate and are unreliable (post-2021 papers are usually absent). Try a list of mirrors in turn; the PDF link is on the article page as a `citation_pdf_url` meta tag or an `<embed>`/`<iframe>`/ `<object>` element. Mirrors often have broken TLS, so disabling certificate verification is the norm here. A proxy can be supplied for restricted networks.

Anna's Archive is **dormant unless `ANNAS_SECRET_KEY` is set**; only its members-only fast JSON API is automatable. The slow tier needs a running FlareSolverr at `FLARESOLVERR_URL` to pass the JS anti-bot wall. Anna's is also the realistic route to a **textbook** (resolve an ISBN to an md5 first).

## Verified behaviour

- Unpaywall responds and is the most reliable OA route (`api.unpaywall.org/v2/<doi>?email=...`), though closed-access papers legitimately have no `url_for_pdf`.
- Sci-Hub and Anna's mirror availability and legality vary by jurisdiction; treat any PDF you obtain as something to validate and to attribute to the source you actually used.

## Validate, always

Never accept bytes on faith — publishers return HTML error pages with a `.pdf` name:

1. starts with the `%PDF-` signature;
2. opens without error and is not encrypted;
3. has at least one page, and page 0 actually loads.

Discard anything else and move on. Report the source you actually used.

## Traps

- **No PDF ≠ no paper.** Closed-access work often yields only metadata + abstract. Say that explicitly rather than reporting failure.
- Do not extract text to "read" a paper — download the PDF and view it, so figures and equations survive.
- Rate-limit your mirror attempts; hammering all mirrors at once gets you blocked faster.
