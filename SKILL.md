---
name: literature-search
title: Find, analyze, read scholarly papers and save them to Zotero
enabled: true
description: >-
  General-purpose scholarly-literature engine: the importable `scholar` Python package, whose functions you call from `uv run python`. Use it to find papers, analyze citations and authors, obtain open-access full text, inspect figures, and manage the Zotero library. The package composes live results from OpenAlex, Semantic Scholar, Crossref, arXiv, PubMed, and Europe PMC.
---

# Literature Search

This is the overview and first instruction file for the skill. The engine is the importable `scholar` package in `scripts/scholar/`. Run it with `uv run python` from `scripts/`; the project is installed editable, so imports and local edits are live.

## Operating model

Every call reaches the configured upstream source live. The package does not maintain a materialized scholarly graph or metadata cache between calls. Records carry identifiers, so the result of one call can seed another call.

Python is the query language. Compose the functions for relational questions such as “which papers do these two authors share?”, citation traversal, and co-authorship. If genuine graph analytics are needed, materialize only the required subgraph transiently for that run; do not add a persistent graph database or a second query-language system.

The one durable store is the user's Zotero library. It is curated state, not a scholarly metadata cache, and it is read live through the Zotero Web API.

## Flexible composition

There is no required sequence, starting point, or set of functions for a task. Select the smallest useful composition and begin wherever the user's question requires:

- consult Zotero early when the task concerns the user's library, existing papers, or durable saves;
- discover papers when new literature is needed;
- analyze authors, citations, related work, or facets when those relationships matter;
- obtain full text or figures when the evidence needs to be read in context;
- save complete metadata and attachments when the user wants to keep a paper.

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
