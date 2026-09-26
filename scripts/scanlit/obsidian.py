"""Obsidian vault integration: create and read paper notes backed by Zotero."""
import os
import pathlib
import re

import frontmatter
from importlib.resources import files
from .zotero import zotero_get


# Use an explicit vault when supplied; otherwise keep notes in the current
# project's vault directory. This also works when scanlit is installed from PyPI.
_DEFAULT_VAULT = pathlib.Path(os.environ.get("OBSIDIAN_VAULT", pathlib.Path.cwd() / "vault")).expanduser()


def _load_template() -> str:
    """Load the packaged Markdown body template on each creation."""
    return files("scanlit").joinpath("templates", "paper.md").read_text(encoding="utf-8")


def _build_body(title: str, abstract: str | None) -> str:
    """Replace {{ title }} and {{ abstract }} in the external .md template once.

    A one-pass replacement avoids interpreting {{ ... }} inside a Zotero title
    or abstract as an additional template variable.
    """
    template = _load_template()
    token = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
    unknown = {match.group(1).strip() for match in token.finditer(template)} - {"title", "abstract"}
    if unknown:
        raise ValueError(f"Unknown paper note template placeholders: {sorted(unknown)}")
    replacements = {"title": " ".join(title.splitlines()),
                    "abstract": (abstract.strip() + "\n\n") if abstract and abstract.strip() else ""}
    return token.sub(lambda match: replacements[match.group(1).strip()], template)


def _canonical_isbn(isbn: str | None) -> str:
    """Remove display hyphens/spaces and verify an ISBN-10 or ISBN-13 checksum."""
    import re
    value = re.sub(r"[-\s]", "", isbn or "").upper()
    if len(value) == 13 and value.isdigit():
        if sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value)) % 10 == 0:
            return value
    elif len(value) == 10 and value[:9].isdigit() and (value[9].isdigit() or value[9] == "X"):
        checksum = sum((10 - i) * (10 if char == "X" else int(char)) for i, char in enumerate(value))
        if checksum % 11 == 0:
            return value
    raise ValueError(f"Book has no valid unambiguous ISBN: {isbn!r}")


def _paper_path(doi: str | None, title: str, *, isbn: str | None = None,
                vault: pathlib.Path | None = None) -> pathlib.Path:
    """Use DOI directories at the vault root; use canonical ISBN for DOI-less books.

    DOI names are case-insensitive; lower-case for stable, deduplicated paths.
    Never substitute a Zotero key or title for an absent/invalid ISBN.
    """
    root = vault or _DEFAULT_VAULT
    if doi and doi.strip():
        value = doi.strip().lower()
        segments = value.split("/")
        if len(segments) < 2 or any(part in ("", ".", "..") or "\\" in part or "\x00" in part
                                    for part in segments):
            raise ValueError(f"Unsafe or malformed DOI for paper note path: {doi!r}")
        return root.joinpath(*segments[:-1], segments[-1] + ".md")
    return root / "Books" / f"{_canonical_isbn(isbn)}.md"


def _paper_metadata(zotero_key: str) -> tuple[dict, str, str | None]:
    """Resolve parent metadata for both article/book keys and attachment keys."""
    item = zotero_get(zotero_key)["result"]["data"]
    parent_key = item.get("parentItem")
    paper = zotero_get(parent_key)["result"]["data"] if parent_key else item
    title = paper.get("title") or item.get("title") or zotero_key
    doi = paper.get("DOI") or None
    if not doi:
        if paper.get("itemType") != "book":
            raise ValueError(f"No DOI for Zotero item {zotero_key}; ISBN-based paths are only for books")
        _canonical_isbn(paper.get("ISBN"))
    return paper, title, doi


def obsidian_create(zotero_key: str) -> dict:
    """Create or find a note at vault/<DOI path>.md, or vault/Books/<ISBN>.md.

    No existing note is ever overwritten, including an empty placeholder.
    Article and attachment keys resolve to parent DOI/ISBN metadata; the key
    remains in YAML front matter. The body comes from templates/paper.md.
    """
    paper, title, doi = _paper_metadata(zotero_key)
    note_path = _paper_path(doi, title, isbn=paper.get("ISBN"))
    if note_path.exists():
        return {"created": False, "path": str(note_path)}
    body = _build_body(title, paper.get("abstractNote") or None)
    metadata: dict = {"zotero_key": zotero_key}
    if doi:
        metadata["doi"] = doi
    authors = [" ".join(filter(None, [c.get("firstName"), c.get("lastName")]))
               for c in paper.get("creators", []) if c.get("creatorType") == "author"]
    if authors:
        metadata["authors"] = authors
    for field, value in (("date", paper.get("date")), ("publisher", paper.get("publisher"))):
        if value:
            metadata[field] = value
    note_path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(body, **metadata)
    rendered = frontmatter.dumps(post) + "\n\n"
    # x-mode is exclusive even if another process creates the path after exists().
    try:
        with note_path.open("x", encoding="utf-8") as destination:
            destination.write(rendered)
    except FileExistsError:
        return {"created": False, "path": str(note_path)}
    return {"created": True, "path": str(note_path), "key": zotero_key,
            "title": title, "doi": doi}


def obsidian_read(zotero_key: str) -> dict:
    """Read a DOI/ISBN-named paper note using the item or attachment's Zotero key.

    Resolve the paper's DOI/title through Zotero. No key-named legacy paths are read.
    """
    paper, title, doi = _paper_metadata(zotero_key)
    note_path = _paper_path(doi, title, isbn=paper.get("ISBN"))
    content: str | None = note_path.read_text(encoding="utf-8") if note_path.exists() else None
    return {"path": str(note_path), "content": content}
