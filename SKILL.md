---
name: literature-search
title: Find, analyze, read scholarly papers and save them to Zotero
enabled: true
description: >-
    General-purpose scholarly-literature engine: the importable `scanlit` Python package, whose functions you import and call directly. Use it to find papers, analyze citations and authors, obtain open-access full text, inspect figures, and manage the Zotero library. The package composes live results from OpenAlex, Semantic Scholar, Crossref, arXiv, PubMed, and Europe PMC.
---

# Literature Search

This is the overview and first instruction file for the skill. The engine is the installable `scanlit` package declared by the repository's `pyproject.toml`. Install it into your active Python environment (if needed), then import and call `scanlit` directly.

## Operating model

Use `scanlit` as a Python library in the active Python execution environment: import the needed functions and call them directly. Do not construct Python source in a string, invoke `python -c`, or wrap ordinary library calls in `subprocess`. If the package is not available in the active environment, install this local project once and then import it normally.

Make work observable. Before a multi-paper operation, display the identifiers that will be processed. Display the returned result after every call; for long operations, use one paper or a small batch at a time and show each result before continuing. Do not hide an entire literature or Zotero workflow in a subprocess and reveal only its final stdout.

Every call reaches the configured upstream source live. The package does not maintain a materialized scholarly graph or metadata cache between calls. Records carry identifiers, so the result of one call can seed another call.

Python is the query language. Compose the functions for relational questions such as “which papers do these two authors share?”, citation traversal, and co-authorship. If genuine graph analytics are needed, materialize only the required subgraph transiently for that run; do not add a persistent graph database or a second query-language system.

The one durable store is the user's Zotero library. It is curated state, not a scholarly metadata cache, and it is read live through the Zotero Web API.

## Flexible composition

There is no required sequence, starting point, or set of functions for a task. Select the smallest useful composition and begin wherever the user's question requires:

- consult Zotero early when the task concerns the user's library, existing papers, or durable saves;
- discover papers when new literature is needed;
- analyze authors, citations, related work, or facets when those relationships matter;
- obtain full text or figures when the evidence needs to be read in context; choose an explicit PDF source when tracing a failed route and validate local files with `pdf_check` (acquisition and validation live together in `scripts/scanlit/pdf.py`);
- save complete metadata and validated attachments when the user wants to keep a paper; check `pdf_errors` and `has_pdf`, not merely the existence of an attachment record.
- for Obsidian notes, DOI slashes are real directories under the vault root; books without a DOI use `vault/Books/<ISBN>.md`. Keep the Zotero key in front matter, not the filename. `obsidian_create` reads `scripts/scanlit/templates/paper.md` and must never modify an existing note, even an empty one.

These are independent options, not gates. A task can use one function, several functions in any order, or none of the listed activities.

Tell the user what was already present versus what is new, and report exclusions, failures, and unresolved uncertainty.

## Progressive disclosure

Read only the files needed for the current task:

- [Function reference](instructions/functions.md) — callable functions, arguments, batching, return contracts, and composition.
- [Workflow guidance](instructions/workflows.md) — the library-first workflow, discovery, verification, warnings, and reporting.
- [Database and documentation map](instructions/databases.md) — databases and support services, API addresses, and official documentation.
- [Analysis guidance](instructions/analysis.md) — ranking, citations, facets, author disambiguation, coauthors, profiling, and analytical limits.
- [Reading guidance](instructions/reading.md) — open-access routing, PDF acquisition, webpage snapshots, and figure extraction.
- [Zotero guidance](instructions/zotero.md) — complete metadata, attachment handling, Zotero reads and writes, backup, and local-versus-remote state.

The [source notes](references/sources.md) and [diagrams](references/) are deeper implementation references. Consult them when a source-specific quirk or composition diagram is relevant.

## Non-negotiable defaults

- Query live upstream sources; do not treat stored notes, prior answers, or cached metadata as authoritative.
- Consult the user's Zotero library when the task involves existing library items, duplicate avoidance, or saving papers; independent discovery does not require a library lookup.
- Keep discovery broad unless the user asks for a year, type, or open-access restriction, and report every narrowing filter and source failure.
- Read the fields and files you retrieve before drawing conclusions.
- Cite titles, authors, dates, venues, identifiers, citation counts, and access status from the source that supplied them.
- Never use emojis. Use Unicode for mathematical notation in Zotero fields and user-facing text.
