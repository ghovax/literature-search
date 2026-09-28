# Related work

"Papers like this one." Two mechanisms, both algorithmic — treat the output as candidates, not answers.

- **OpenAlex** related works: read `related_works` on the work, then fetch them by id
  (`https://api.openalex.org/works?filter=openalex_id:W1|W2|...&per-page=<n>`).
- **Semantic Scholar** recommender:
  `https://api.semanticscholar.org/recommendations/v1/papers/forpaper/<id>?fields=title,year,authors,abstract,venue,citationCount,externalIds,openAccessPdf&limit=<n>`

Prefer OpenAlex by default; use Semantic Scholar when the recommendations look stale, and fall back to
OpenAlex if it returns nothing. **Always check topical fit before presenting** — neither method knows
what you mean by "related", only what co-cites or co-occurs.
