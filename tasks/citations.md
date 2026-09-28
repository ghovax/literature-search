# Citation graph: what cites a paper, and what it cites

Two directions, and two providers with different strengths.

## Forward — works that cite it

- OpenAlex: `https://api.openalex.org/works?filter=cites:<W-id>&sort=cited_by_count:desc&per-page=<n>&mailto=<you>`
- Semantic Scholar (adds the sentences where the citation occurs):
  `https://api.semanticscholar.org/graph/v1/paper/<id>/citations?fields=contexts,isInfluential,title,year,authors,abstract,venue,citationCount,externalIds&limit=<n>`

## Backward — its reference list

- OpenAlex: read `referenced_works` on the work, then fetch those ids:
  `https://api.openalex.org/works?filter=openalex_id:W1|W2|W3&per-page=<n>` (batch ~50 ids per call).
- Semantic Scholar: `.../paper/<id>/references?fields=...`.

## Choosing a provider

Use **OpenAlex** for breadth and counts. Use **Semantic Scholar** when the *relationship* matters —
`isInfluential` flags the citations the citing paper leans on, and `contexts` gives the actual
sentences, which is what you want for "how is this used" questions. Semantic Scholar wants a DOI
passed as `DOI:<doi>` (or `ARXIV:<id>`); ids containing `/` must be URL-encoded.

## Traps

- Citation counts are a **lower bound**. Neither index is exhaustive, and they disagree; never present
  one count as the count.
- `referenced_works` can be long and is capped by your `n`.
- The graph endpoints need an OpenAlex-indexed id. A pure arXiv id will not traverse; resolve it to a
  DOI first, or use Semantic Scholar.
- Semantic Scholar may be unavailable without a key (it 429s); if you fall back to OpenAlex, note that
  you lost the contexts and influential flags.
