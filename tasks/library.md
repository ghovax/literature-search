# Library and notes

Keep one durable record of what you have read, so papers and their notes are findable and citeable.

## Zotero

Everything goes through the Zotero Web API: `https://api.zotero.org/users/<libraryID>` (or `/groups/<id>`), with `Zotero-API-Key` and `Zotero-API-Version: 3` on every call.

Two facts to internalise:

- **The library is the one durable store**; a local `zotero.sqlite` is a cache that may lag it.
- **Writes are concurrency-checked.** Send `If-Unmodified-Since-Version` with the current library version; a `412` means someone wrote first — re-read the version and retry. Any response's `Last-Modified-Version` header is that version.

**Reading.** Items come in pages (`/items`, with `start`/`limit`), filterable by item type, tag, a quicksearch query, or a collection. A collection's subcollections are separate collections, so recurse for the whole tree. Fetch a single item by key, and its children (notes, attachments) via `/items/<key>/children`. For dedup you only need the key, DOI, title, and type.

**Saving a paper.** The goal is a *complete* item, not a stub: title; every author; journal; year, volume, issue, pages; DOI, ISSN, URL, language; a clean abstract; and the PDF whenever one could be retrieved.

1. **Dedup by DOI against the live library first** — skipping this is how you end up with five copies of the same paper, and re-running must be safe.
2. **Enrich from Crossref** when a DOI exists: structured authors, container, volume/issue/pages, ISSN, date, language, and abstract (strip its markup).
3. **Create** the item, in batches the API accepts. Fill every field you have; on a later edit fill only what is missing and never overwrite good data with worse.
4. **Attach the PDF** if you have one.

Use Unicode symbols in Zotero fields, not LaTeX (`H₂`, `Δ`, `≈`, `≤`).

**Attaching a PDF.** Creating the attachment item and uploading its bytes are separate steps, and the file endpoints are guarded differently from item writes (so they are safe to run in parallel). Check the file is a real PDF first — a broken icon almost always means an HTML page was uploaded under a PDF name.

**Updating and deleting.** Updating is a PATCH: send the item's `key` plus only the fields you want changed, where an empty value clears a field. Deleting takes a list of keys.

## Obsidian notes

One note per paper, at a path derived from its identity so citations can be wiki-links that resolve.

- A paper **with a DOI** lives at `<vault>/<doi>/...`, its slashes as real directories (`10.1038/nmat1885` → `<vault>/10.1038/nmat1885.md`).
- A **DOI-less book** goes under `<vault>/Books/<ISBN>.md`, with a valid ISBN.
- The Zotero key belongs in the front matter, never in the filename.

The note's front matter carries the Zotero key, plus DOI, authors, date, and publisher when known. The body is the title, the abstract, and then a `## Comments` heading — that heading is the anchor, and reading notes accumulate under it. Keep the shape stable so notes stay uniform across the vault.

- **Never overwrite an existing note, even an empty one.** Create only; if the path exists, leave it. These files are hand-edited.
- Take the metadata from the library, so the note agrees with the Zotero item it points at.
- To read a note back, resolve its DOI/ISBN through the library rather than guessing the filename.
- Cite other papers as `[[<doi>]]`, not by author name, so the link resolves.

## Report state honestly

- A file being **uploaded to the server** and being **present in the desktop client's local storage** are different things. A successful upload does not mean the app has the file, and a local file does not mean the server has it — never infer one from the other.
- Say how many items dedup skipped and why, and which write failed if one did.
- The API sees the *remote* library; it can diverge from the user's local app until sync. Do not assume they match.
