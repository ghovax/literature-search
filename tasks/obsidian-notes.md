# Obsidian notes for papers

One note per paper, so citations can be wiki-links that resolve.

## Layout

- A paper note lives at `<vault>/<doi-prefix>/<doi-suffix>.md` — **DOI slashes are real directories**.
  `10.1038/nmat1885` → `<vault>/10.1038/nmat1885.md`.
- Lowercase the DOI path for stability.
- A **book without a DOI** uses `<vault>/Books/<ISBN>.md`, with a validated ISBN (checksum).
- The **Zotero key lives in the front matter**, never in the filename.

## Note shape

Front matter with `zotero_key` (always), plus `doi`, `authors`, `date`, `publisher` when known. Then:

```markdown
# <Title>

<abstract>## Comments

```

The `## Comments` heading is the anchor: that is where reading notes accumulate. Keep the body template
stable so notes stay uniform across the vault.

## Rules

- **Never overwrite an existing note, even an empty one.** Create-only; if the path exists, leave it be.
  This matters because the user hand-edits these files.
- Resolve the paper's metadata (title, DOI/ISBN, creators, abstract) **from the library** so the note
  agrees with the Zotero item, and keep the same key in the front matter.
- To read a note back, resolve its DOI/ISBN through the library and open that path — do not guess the
  filename.
- Cite other papers as `[[<doi>]]` (the DOI string), not as author names, so the link resolves.
