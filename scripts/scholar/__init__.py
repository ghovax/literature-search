"""Unified multi-source scholarly engine.

The package covers discovery, analysis, reading, and library management behind
plain functions: finding papers (`search`), analyzing them (`lookup`, `citations`, `similar`,
`facets`, `find_authors`, `coauthors`, `author_works`, `author_profile`),
and reading their full text and figures (`fulltext`,
`figures`), plus full Zotero Web API management (`zotero_*`). Each returns a
plain dict and every result record carries an `ids` object, so the output of one
call feeds the next.

This package is the interface: import it and call its functions from Python run
with `uv run python` from the project root (the project is installed editable, so
`import scholar` works with no sys.path juggling and edits are live).

Batch by default: every discovery, analysis, and reading function takes its primary argument (a query, a
paper id, an author) either as a single value  returning one result dict  or
as a list, in which case the whole list runs concurrently and the results come
back in input order under "results". The Zotero functions are likewise batch-first.

Credentials are read from the environment or a project .env: S2_API_KEY for
discovery; ZOTERO_API_KEY / ZOTERO_LIBRARY_ID / ZOTERO_LIBRARY_TYPE
for Zotero; optional CORE_API_KEY, ANNAS_SECRET_KEY, FLARESOLVERR_URL for
additional full-text routes.
"""
from .analyze import (
    author_profile,
    author_works,
    citations,
    coauthors,
    facets,
    find_authors,
    lookup,
    similar,
)
from .common import configure_logging
from .find import search
from .obsidian import obsidian_create, obsidian_read
from .read import book_fulltext, figures, fulltext, webpage_snapshot
from .zotero import (
    zotero_attach,
    zotero_collections,
    zotero_create,
    zotero_delete,
    zotero_get,
    zotero_items,
    zotero_save,
    zotero_update,
)

__all__ = [
    # Discovery, analysis, and reading (each accepts a single id/query OR a list for batching).
    "search", "lookup", "citations", "similar", "facets", "fulltext", "figures",
    "book_fulltext", "webpage_snapshot",
    "find_authors", "coauthors", "author_works", "author_profile",
    # Obsidian vault integration.
    "obsidian_create", "obsidian_read",
    # Zotero Web API  full CRUD plus PDF upload, every call batched.
    "zotero_save", "zotero_create", "zotero_update", "zotero_delete",
    "zotero_attach", "zotero_items", "zotero_collections", "zotero_get",
    "configure_logging",
]
