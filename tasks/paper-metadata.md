# One paper: metadata from an identifier

You have a DOI, arXiv id, PMID, PMCID, or an OpenAlex `W...` id, and want the record.

## Resolve

- DOI, PMID, PMCID, or `W...` → OpenAlex:
  `https://api.openalex.org/works/https://doi.org/<doi>?mailto=<you>`
  `https://api.openalex.org/works/pmid:<id>?mailto=<you>`
  `https://api.openalex.org/works/pmcid:<id>`
  `https://api.openalex.org/works/<W-id>`
- arXiv id (or the `10.48550/arxiv.XXXX` DOI) → arXiv itself:
  `http://export.arxiv.org/api/query?id_list=<id>` (Atom XML).
- Crossref, when you want publisher-side fields verbatim:
  `https://api.crossref.org/works/<doi>`.

## Normalize

Map to the common record shape (`00-overview.md`). Two fields need care:

- **Abstract.** OpenAlex returns an inverted index (word → positions), not prose. Rebuild it by
  sorting the `(position, word)` pairs and joining. Some records have none.
- **Authors.** OpenAlex gives authorship entries with `display_name`; Crossref separates `given`
  and `family`. Keep one convention.

## Ids you should capture

Persist every id the source gives (`doi`, `arxiv`, `pmid`, `pmcid`, `openalex`) — the merged set is what
lets later steps avoid a second lookup, and it is what the Zotero dedup keys on.

## Traps

- A DOI lookup can 404 if the work is not in that index; fall back to another source, and say which.
- OpenAlex invents an id for anything it indexes, but its abstracts are often absent for older or
  closed-access work. Absence is not evidence of no abstract.
- If several sources disagree on year/venue, prefer the publisher record (Crossref) and note the conflict.
