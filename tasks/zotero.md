# Zotero library: read, save, and maintain

Everything is the Zotero Web API. Base:
`https://api.zotero.org/users/<libraryID>` (or `/groups/<id>` for a group library).
Send `Zotero-API-Key: $ZOTERO_API_KEY` and `Zotero-API-Version: 3` on every call.

Two facts to internalise:

- **The library is the one durable store.** Treat a local `zotero.sqlite` as a *cache* that may lag the
  server; the API is the source of truth.
- **Writes are concurrency-checked.** Send `If-Unmodified-Since-Version: <Last-Modified-Version>`; a
  `412 Precondition Failed` means someone else wrote first — re-read the version and retry.

## Read

- Whole library / quicksearch / one collection:
  `GET /items?limit=100&start=0&format=json&include=data` (add `itemType=-attachment` to skip files,
  `q=<text>&qmode=everything` to search, `tag=<tag>` to filter).
- One collection: `GET /collections/<key>/items?...`; subcollections are separate collections, so
  recurse via each collection's `parentCollection`.
- Specific items by key: `GET /items/<key>`; children (notes, attachments): `GET /items/<key>/children`.
- Collections list (to find a key or the tree): `GET /collections?limit=100`.
- `Last-Modified-Version` on any response is the library version — cache it, it is your write token.

Compact the results for dedup: `{key, doi, title, item_type}`. Use the full `data` object only when you
need every field.

## Save a paper (the common write)

The goal is a **complete** item, not a stub. A saved paper has: title; every author; journal; year,
volume, issue, pages; DOI, ISSN, URL, language; a clean abstract; and the PDF whenever one could be
retrieved.

1. **Dedup by DOI against the live library** first (`GET /items?q=<doi>` or scan the DOI map). Skipping
   this is how you get five copies of the same paper. Re-running must be safe.
2. **Enrich from Crossref** when a DOI exists (`https://api.crossref.org/works/<doi>`): structured
   authors, container title, volume/issue/pages, ISSN, date, language, and the abstract. Crossref wraps
   abstracts in JATS/HTML tags — strip them to plain text.
3. **Create** with `POST /items`, a JSON array of item objects, **at most 50 per request**. Minimal
   body per item for a journal article: `itemType` `journalArticle`, `title`, `creators`
   (`{creatorType:"author", firstName, lastName}`), `date`, `publicationTitle`, `volume`, `issue`,
   `pages`, `DOI`, `url`, `abstractNote`, `language`, `tags` (`[{tag:"..."}]`), `collections` (keys).
4. **Attach the PDF** (below) if you have one.

Fill only missing fields when updating; never overwrite good data with worse. **Do not put LaTeX in
Zotero fields** — use Unicode symbols (`H₂`, `Δ`, `≈`, `≤`, `10⁸`).

## Attach a PDF

Two steps, because the file endpoints are version-guarded differently from item writes:

1. `POST /items` with an attachment template: `itemType:"attachment"`, `parentItem:<key>`,
   `linkMode:"imported_file"`, `contentType:"application/pdf"`, `filename`, `title`.
2. Upload bytes:
   a. `POST /items/<attachmentKey>/file` with `If-None-Match: *` and form fields `md5`, `filename`,
      `filesize`, `mtime` → returns `{exists}` or `{url, prefix, suffix, contentType, uploadKey}`.
   b. If not `exists`: `POST <url>` with body `prefix + bytes + suffix` and the returned `contentType`.
   c. `POST /items/<attachmentKey>/file` with `upload=<uploadKey>` to register.
   These file endpoints use `If-None-Match` rather than the library version, so they are safe to run in
   parallel.

**Validate the PDF before uploading** (`%PDF-` signature, parseable, ≥1 page). A gray/broken icon almost
always means an HTML page was uploaded under a PDF name.

## Update and delete

- Update: `POST /items` with objects that carry their `key` (PATCH semantics — only supplied fields
  change; an empty string/array clears a field). Same 50-per-request limit and version precondition.
- Delete: `DELETE /items?itemKey=<k1>,<k2>,...`, at most 50 keys, with the version precondition.

## State you must report honestly

- **`remote_uploaded`** (an attachment row with an md5, registered on the server) and
  **`locally_cached`** (bytes present in the desktop client's `storage/` folder) are different things.
  A successful upload does not mean the desktop app has the file, and a local file does not mean the
  server has it. Never infer one from the other.
- If dedup skipped items, say how many and why. If a write failed, report which index/key failed.
- The API sees the *remote* library. If the user is looking at their local Zotero app, the two can
  diverge until sync. Do not assume they match.
