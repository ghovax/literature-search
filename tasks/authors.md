# People: disambiguation, collaborators, and an author's works

OpenAlex-only. Names are not unique, so **always disambiguate before you act on a name**.

## Find a candidate

`https://api.openalex.org/authors?search=<name>&per-page=<n>&mailto=<you>`

Each candidate carries `id` (`A...`), `display_name`, `orcid`, `works_count`, `cited_by_count`, `summary_stats.h_index`, last-known institutions, and topics. Pick by field match and institution, not by name alone. You can fetch directly by id: `https://api.openalex.org/authors/<A-id>`.

## Co-authors

Pull a slice of the author's works and tally the other authorship ids: `https://api.openalex.org/works?filter=authorships.author.id:<A-id>&per-page=200&mailto=<you>` Count each collaborator id, drop the author, keep the top N, then enrich with the author-by-id endpoint. Order by joint-paper count, and optionally re-rank by h-index/citations. **This samples up to ~200 works** — an author with more may have collaborators you missed. Say so.

## An author's works

`https://api.openalex.org/works?filter=authorships.author.id:<A-id>&sort=cited_by_count:desc&per-page=<you>` Add `from_publication_date` / `to_publication_date` for a window. To enumerate *everything*, page with the `cursor=*` parameter (`&cursor=*` then follow `meta.next_cursor`) rather than a fixed `per-page`.

For two people's joint output: pull both author's works and intersect on the co-author's id.

## Traps

- Wrong-twin risk is real: an author id can be a merge of two people, or split across two ids. Cross-check with ORCID and institution when a decision matters.
- `per-page` maxes at 200; there is no offset paging beyond 10 000 results, so use the cursor.
