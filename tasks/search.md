# Discovery: finding papers on a topic

You have a topic and no id. Query several databases in parallel, merge the duplicates, and rank —
no single source is complete, and their coverage differs by field.

## Sources

| Source | Endpoint | Notes |
| --- | --- | --- |
| OpenAlex | `https://api.openalex.org/works?search=<q>&per-page=<n>&mailto=<you>` | broadest; facets, filters, citation counts |
| Crossref | `https://api.crossref.org/works?query.bibliographic=<q>&rows=<n>&mailto=<you>` | publisher metadata; no abstracts for many records |
| Semantic Scholar | `https://api.semanticscholar.org/graph/v1/paper/search?query=<q>&limit=<n>&fields=title,year,venue,authors,abstract,citationCount,externalIds,openAccessPdf` | good relevance; send `x-api-key` if you have one |
| Europe PMC | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json&resultType=core&pageSize=<n>` | life sciences; `<q>` also takes `PUB_YEAR:[a TO b]`, `OPEN_ACCESS:Y` |
| arXiv | `http://export.arxiv.org/api/query?search_query=all:<q>&max_results=<n>` | preprints; returns Atom XML |
| PubMed | esearch then esummary (see below) | biomedical |

PubMed is two steps:
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<q>&retmax=<n>&retmode=json&sort=relevance`
gives an `IdList`; then
`.../esummary.fcgi?db=pubmed&id=<comma-joined ids>&retmode=json`.
Send a `tool`/`email` pair if you are making many calls.

## Filters (apply only when asked)

- OpenAlex: `filter=from_publication_date:2020-01-01,to_publication_date:2024-12-31,is_oa:true,type:article`
- Crossref: `filter=from-pub-date:2020-01-01,until-pub-date:2024-12-31,type:journal-article`
- Sort: OpenAlex `sort=cited_by_count:desc`; Crossref `sort=is-referenced-by-count&order=desc`.
- Leave the year window, type, and open-access flags **unset** by default. Set them only when the user
  asks, and say so when you do — each one silently drops matching papers.

## Merge and rank

1. De-duplicate by DOI, then by identical normalized title (lowercase, alphanumerics only; ignore
   titles under ~10 characters as too generic). A preprint and its published version often carry
   different DOIs — match them on title.
2. Keep the most complete field across duplicates (longest abstract, largest author list, lowest
   source rank, union of `ids`).
3. Rank by a weighted blend of: retrieval rank within each source, log(citations), recency,
   how many sources found it, and venue authority. When the user asks for "most cited" or "newest",
   sort by that field directly instead.

## Traps

- **arXiv is the flakiest source.** As of this writing `export.arxiv.org` returns `406` even with a
  browser `User-Agent`, and the `arxiv` Python client fails the same way. Do not depend on it as your
  only route: resolve preprints through OpenAlex/Semantic Scholar or the arXiv *listing pages* instead,
  and record when arXiv was skipped.
- **Crossref** returns `429` readily under parallel load; back off and retry. Its `query.bibliographic`
  is fuzzy — verify that the returned title actually matches.
- Every source caps results, so *more matching papers exist beyond your `n`*. Raise the limit to widen,
  and never present the top page as exhaustive.
- **Semantic Scholar without `S2_API_KEY` repeatedly returns `429`** (verified: three consecutive 429s).
  With a key it is fine; without one, treat it as best-effort and note the gap.
- Report per-source failures. A timeout or 406/429 is not "no results".
