# Literature tasks: operating manual

This folder replaces the `scanlit` Python package. Each file describes one task, and each is self-contained: the endpoints, the parameters that matter, and the traps. Work them with a shell (`curl`, `jq`) or a short Python snippet — there is nothing to import.

## Files

| Task | File | Use it when |
| --- | --- | --- |
| Discovery | `search.md` | you need papers on a topic and have no id yet |
| One paper | `paper-metadata.md` | you have a DOI/arXiv/PMID/OpenAlex id and want its metadata |
| Citation graph | `citations.md` | forward (citing) or backward (references) traversal |
| Related work | `similar-papers.md` | "papers like this one" |
| Corpus shape | `facets.md` | counts by year, venue, institution, type, ... |
| People | `authors.md` | disambiguate a name, co-authors, an author's works |
| Full text | `fulltext.md` | find and download a PDF |
| Figures | `figures.md` | pull figure images out of a PDF |
| Web pages | `webpage-snapshot.md` | archive a URL |
| Library | `zotero.md` | read/write the Zotero library |
| Notes | `obsidian-notes.md` | create/read the vault note for a paper |

## Conventions that apply everywhere

**Credentials** live in the environment or a project `.env` (never hard-code them, never print them):

- `S2_API_KEY` — Semantic Scholar; without it you share an anonymous pool and will hit 429s.
- `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (`user` or `group`) — Zotero Web API.
- `CORE_API_KEY` — higher CORE rate limit (full-text route only).
- `ANNAS_SECRET_KEY`, `FLARESOLVERR_URL` — only the optional Anna's Archive routes.
- `OBSIDIAN_VAULT` — vault root for notes (a DOI note lives at `<vault>/<doi-prefix>/<doi-suffix>.md`).

**Be polite.** OpenAlex and Crossref both accept a contact address and give better service when you send it (`mailto=` on OpenAlex, `mailto=` on Crossref); use the real one, not a placeholder.

**Record shape.** Normalize everything you keep to the same fields, so any step can feed any other:

```json
{"title": "...", "authors": ["..."], "year": 2022, "venue": "...", "abstract": "...",
 "citations": 0, "ids": {"doi": "...", "arxiv": "...", "pmid": "...", "openalex": "W..."}}
```

`ids` is the point: it is what you pass to the next call.

**Identifiers are interchangeable.** OpenAlex resolves a DOI, PMID, PMCID, or its own `W...` id; give it `https://doi.org/<doi>` or `pmid:<id>`. arXiv is the exception — resolve it through arXiv itself, because OpenAlex indexes arXiv ids unreliably.

**Say what you did.** Report which sources answered, which failed or timed out, and what you filtered out. A silent narrowing (year window, open-access only, per-source result cap) is how a literature search quietly lies to you.

**Read before concluding.** Fetch the record; do not infer fields from the query. If a source gives no abstract, record that rather than writing one.
