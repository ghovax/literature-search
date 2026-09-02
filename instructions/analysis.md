# Analysis, ranking, and analytical limits

## Ranking

`search` uses a composite ranking unless an explicit citation or date sort is requested. You can re-sort returned records yourself by citations or year. A citation sort is useful for impact, not topicality: a broad query can surface highly cited but off-topic papers.

Mind the field names: normalized paper records use `citations`; OpenAlex author records use `cited_by_count`.

## Authors and coauthors

Names are ambiguous. Use `find_authors(name)` first when a person could map to more than one researcher. Compare OpenAlex id, ORCID, affiliation history, works count, h-index, and name variants before choosing a candidate. Then pass the selected OpenAlex id to `author_profile`, `author_works`, or `coauthors`.

`coauthors` counts collaborators by OpenAlex author id, not by display name. `author_works(author, coauthor=...)` returns only the two authors' shared works. If a task needs a complete coauthor sweep, use a sufficiently large `maximum_results` or compose a direct OpenAlex cursor-paged fetch and aggregate client-side. Do not assume that a name string identifies one person.

## Author profiles and themes

When the question is about expertise, impact, or research themes, do not infer the answer from titles alone. Read the OpenAlex author record's topics, concepts, summary statistics, affiliations, and year ranges, then cross-check representative works and abstracts.

Use this composition:

1. `author_profile(author)` for topics, concepts, metrics, and affiliation history.
2. Compare `works_count` with the number returned by `author_works`; raise `maximum_results` if the sweep is incomplete.
3. Use `author_works(author, sort="citations")` for representative papers under the relevant topics.
4. Inspect outliers: off-field papers, suspiciously early papers, unexpected institutions, and duplicate author records.

## Abstracts, topics, and citations

Always pull abstracts and topics for an analysis. An abstract carries the claim and method that a title omits. Cite the source of the abstract and say when only an abstract was available. Citation counts differ across providers; treat them as approximate and use a citation traversal when the exact graph matters.

## Facets and visualization

`facets` is an OpenAlex-only operation. State that its counts do not represent an aggregate across all discovery databases. For charts, timelines, heatmaps, or other bibliometric visualizations, use the separate visualization capability rather than hand-rolling chart markup in this skill.

## Limits to state explicitly

- Public scholarly APIs generally search titles, abstracts, and metadata, not the body of every PDF.
- The unified `search` function takes one free-text query per source; compose several narrower searches when needed.
- Source result caps mean that a returned list is not necessarily exhaustive unless the operation explicitly cursor-pages the source.
- Citation counts and coverage differ by database.
- Full text may not exist or may be inaccessible even when metadata does.
- Filters such as year, type, and open-access status narrow recall and must be reported.
- Related-work and recommendation algorithms are leads, not proof of topical fit; verify the retrieved abstracts.

Never silently turn an incomplete source response into an exhaustive claim.
