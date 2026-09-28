# Web pages: archive a URL

Save a faithful artifact of a page, for attaching to a reference or reading later.

**Preferred: render to PDF with headless Chromium** (Playwright: `page.goto(url, wait_until="load")`, a short wait for lazy content, then `page.pdf(print_background=True)`). This handles JavaScript-heavy sites with no per-site special cases, and produces a self-contained document.

**Fallback: a raw HTML snapshot** (a single GET) only when the browser is unavailable or the render fails. Say which one you produced.

## Traps

- Playwright needs its browser installed; if it is missing the render silently degrades, so check.
- Headless rendering still misses login walls, infinite scroll, and consent banners — note anything the snapshot obviously lacks.
- Verify the output is a real PDF (starts `%PDF-`), not an error page.
