# Finding papers

Goal: get from a topic or an identifier to the papers you want, with enough metadata to act on them.

## Discovery: a topic, no id yet

Query several databases — no one is complete, and their coverage differs by field:

| Source | Endpoint |
| --- | --- |
| OpenAlex | `https://api.openalex.org/works?search=<q>&per-page=<n>&mailto=<you>` |
| Crossref | `https://api.crossref.org/works?query.bibliographic=<q>&rows=<n>&mailto=<you>` |
| Semantic Scholar | `https://api.semanticscholar.org/graph/v1/paper/search?query=<q>&limit=<n>&fields=title,year,venue,authors,abstract,citationCount,externalIds,openAccessPdf` |
| Europe PMC | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json&resultType=core&pageSize=<n>` |
| arXiv | `http://export.arxiv.org/api/query?search_query=all:<q>&max_results=<n>` |
| PubMed | `eutils.ncbi.nlm.nih.gov/entrez/eutils/` — esearch then esummary |

Send OpenAlex and Crossref whatever even made-up contact address (`mailto=`). Search broadly by default: a year window, a publication type, or open-access-only each silently drops matching papers, so apply a filter only when the user asks and say that you did.

Merge the results: de-duplicate by DOI, then by title (a preprint and its published version often share a title but not a DOI), keeping the most complete values where records overlap. Rank by relevance and impact, or by citations/date when the user asks for those.

## One paper: an identifier

OpenAlex resolves a DOI, PMID, PMCID, or its own `W...` id at `https://api.openalex.org/works/<id>`; Crossref (`https://api.crossref.org/works/<doi>`) gives publisher-side fields verbatim. arXiv ids are the exception — resolve them through arXiv itself, since OpenAlex indexes them unreliably.

Normalize to the record shape in `SKILL.md`. Two fields need care: OpenAlex returns abstracts as an inverted index rather than prose, so reconstruct them; and sources disagree on author structure, so pick one convention. Keep every id the source gives — later steps and the Zotero dedup key on that set.

## Citation graph

Forward (who cites it) and backward (what it cites):

- OpenAlex — `filter=cites:<W-id>` for citing works; the work's `referenced_works` for references. Broad coverage; good for counts.
- Semantic Scholar — its `citations` / `references` endpoints. Use when the *relationship* matters: `isInfluential` flags the citations that paper leans on, and `contexts` gives the actual sentences, which answers "how is this used".

## Related work

Both mechanisms are algorithmic, so treat their output as candidates: OpenAlex's `related_works`, or Semantic Scholar's recommender (`.../recommendations/v1/papers/forpaper/<id>`). Prefer OpenAlex; fall back to the other if it returns nothing. Check topical fit before presenting — neither knows what *you* mean by "related".

## Corpus shape

For "how much / when / where" rather than a list, group instead of listing: OpenAlex `group_by=<field>` over year, venue, institution, type, open-access status, topic, or country. The counts describe one index's view, not the literature — say so.

## People

OpenAlex only. Names are not unique, so disambiguate before acting: search `https://api.openalex.org/authors?search=<name>` and pick by field and institution, not by name alone.

- **An author's works**: `https://api.openalex.org/works?filter=authorships.author.id:<A-id>`, sorted by citations or filtered by a date window. To enumerate everything, page with the `cursor=*` parameter rather than taking the first page. For two people's joint output, intersect their works on the co-author's id.
- **Collaborators**: tally co-authors across the author's works and keep the frequent ones — you only see a sample of the works, so say when a long record may hide collaborators.
- **Full profile**: fetch the author by id for every topic, the concept scores, and the affiliation history.

## Traps

- **arXiv is the flakiest source.** Its API currently returns `406` even with a browser user-agent, and the `arxiv` client fails the same way. Do not make it your only route; resolve preprints through OpenAlex or Semantic Scholar, and record when arXiv was skipped.
- **Crossref** returns `429` under parallel load — back off and retry. Its query is fuzzy, so check the returned title actually matches.
- **Semantic Scholar without `S2_API_KEY` repeatedly returns `429`**; treat it as best-effort and note the gap. If you fall back to OpenAlex for citations, say that you lost the contexts and influential flags.
- Every source caps its results, so more matching papers exist beyond your `n` — never present the first page as exhaustive.
- Citation counts are a **lower bound**; the indices are not exhaustive and they disagree, so never present one count as *the* count.
- A lookup can 404, and a missing abstract is not evidence that none exists.
- A wrong author id can merge two people or split one across two. Cross-check ORCID and institution when a decision matters.
- Report per-source failures: a timeout or 406/429 is not "no results".
