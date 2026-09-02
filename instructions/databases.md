# Databases and official documentation

Use this reference to choose the right upstream source and find its current documentation. The package's discovery fan-out queries the six sources in the first table. The later table lists support services used for identifiers, open-access routing, and the user's library; they are not all topical discovery databases.

## Discovery databases

| Source | API address | Official documentation | Query for |
| --- | --- | --- | --- |
| OpenAlex | `https://api.openalex.org/` | [API overview](https://help.openalex.org/api/endpoints/), [search](https://help.openalex.org/api/searching/), [semantic search](https://help.openalex.org/api/semantic-search/), [filters](https://help.openalex.org/api/filtering/), [paging](https://help.openalex.org/api/paging/), [authentication](https://help.openalex.org/api/authentication/) | Broad scholarly catalog, structured filters, authors, institutions, citations, facets, and true embedding search via `/works?search.semantic=...`. |
| Semantic Scholar | `https://api.semanticscholar.org/graph/v1/` | [API overview](https://www.semanticscholar.org/product/api), [tutorial](https://webflow.semanticscholar.org/product/api/tutorial), [API reference](https://api.semanticscholar.org/api-docs/) | Relevance-ranked paper search, abstracts, TLDRs, citation graph, recommendations, and SPECTER2-related data. |
| Crossref | `https://api.crossref.org/v1/` | [REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [filters](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/), [access and authentication](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/) | Canonical DOI metadata, publisher-deposited references, funders, licenses, and DOI lookup. |
| arXiv | `https://export.arxiv.org/api/query` | [arXiv API help](https://info.arxiv.org/help/api/index.html) | Physics, mathematics, computer science, and other preprints, including free PDF routes. Use HTTPS. |
| PubMed / NCBI E-utilities | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` | [E-utilities help](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Biomedical records through the `esearch` → `esummary`/`efetch` sequence. |
| Europe PMC | `https://www.ebi.ac.uk/europepmc/webservices/rest/` | [REST service documentation](https://www.ebi.ac.uk/europepmc/webservices/rest/) | Biomedical search with abstracts, citation counts, PMCID, open-access flags, references, and full-text XML. |

## Supporting metadata and full-text services

| Service | API or content address | Official documentation | Use |
| --- | --- | --- | --- |
| Unpaywall | `https://api.unpaywall.org/v2/` | [REST API](https://unpaywall.org/api) | Resolve a DOI to legal open-access locations; requests require an email parameter. |
| PMC / Europe PMC full text | `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML` | [Europe PMC REST service](https://www.ebi.ac.uk/europepmc/webservices/rest/) | Retrieve full-text XML for a PMCID. Keep the `PMC` prefix. |
| bioRxiv / medRxiv | `https://api.biorxiv.org/` | [bioRxiv API](https://api.biorxiv.org/) | Resolve `10.1101/...` preprint DOIs to JATS XML. |
| CORE | `https://api.core.ac.uk/v3/` | [CORE API](https://core.ac.uk/services/api) | Search open-access repositories and locate downloadable full text. `CORE_API_KEY` raises the rate limit. |
| Zotero Web API | `https://api.zotero.org/` | [Zotero Web API](https://www.zotero.org/support/dev/web_api/v3/start) | Read and write the user's durable, curated library. |

The implementation also contains optional fallback routes for Sci-Hub and Anna's Archive. They are not discovery backends and have no stable official documentation that should be treated as a source of truth. Read the [reading guidance](reading.md) and [source notes](../references/sources.md) before enabling or reporting those routes.

## Selection rules

- Use OpenAlex for structured author, institution, citation, facet, and semantic-search questions.
- Use Semantic Scholar when relevance, recommendations, TLDRs, or citation contexts matter.
- Use Crossref to verify DOI metadata, not as the only source for topical relevance.
- Use arXiv for preprint-heavy physics, mathematics, and computer-science searches.
- Use PubMed or Europe PMC for biomedical coverage; Europe PMC is usually the easier all-in-one route when abstracts, PMCID, and full-text links are needed.
- Use Unpaywall, PMC, bioRxiv/medRxiv, or CORE to locate legal full text after discovery.
- Keep the user's Zotero library separate from upstream discovery: it is the first context check and the destination for durable saves.

## Important source quirks

The deeper, implementation-verified [source notes](../references/sources.md) cover OpenAlex abstract reconstruction, source-specific search behavior, Semantic Scholar key handling, available full-text routes, and Zotero transport details.
