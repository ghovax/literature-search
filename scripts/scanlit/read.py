"""Reading interface: fulltext, book PDFs, snapshots, and figure extraction."""
import functools
import pathlib
import re
import tempfile
from typing import Any

import fitz  # PyMuPDF is published under its historical import name, "fitz".
import pyalex

from .analyze import _author_email, _resolve_work
from .common import (
    _batch_summary,
    _parallel_map,
    batchable,
    logger,
)


from .pdf import (  # re-export private helpers for existing internal callers
    _acquire_book, _acquire_pdf, _download, _resolve_fulltext_routes,
)
from .pdf import validate_pdf, validate_pdf_file


def _render_pdf_playwright(url: str) -> bytes | None:
    """Render a URL to a self-contained PDF with headless Chromium (Playwright).

    Faithful for any site, including JS-rendered pages — the page is loaded in a real browser and
    printed to PDF with backgrounds. Returns None (and logs) if Playwright or its browser is missing
    or the render fails, so the caller can fall back. Requires `playwright` and a Chromium install
    (`uv run playwright install chromium`).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed; cannot render %s to PDF (run: uv run playwright install chromium)", url)
        return None
    try:
        with sync_playwright() as play:
            browser = play.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(url, wait_until="load", timeout=60000)
                page.wait_for_timeout(1500)  # let late/lazy content settle before printing
                data = page.pdf(format="A4", print_background=True,
                                margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"})
            finally:
                browser.close()
        return data if data[:4] == b"%PDF" else None
    except Exception as error:  # noqa: BLE001
        logger.warning("Playwright render failed for %s: %s", url, error)
        return None


def _acquire_webpage(url: str) -> tuple[bytes | None, str, str | None]:
    """Return (bytes, extension, source) for a webpage artifact.

    Always render the page to a self-contained PDF with headless Chromium (Playwright) — faithful for
    any site, including JS-heavy ones, with no per-site special cases. Falls back to a raw single-fetch
    HTML snapshot only if the browser is unavailable or the render fails.
    """
    if (data := _render_pdf_playwright(url)) is not None:
        return data, ".pdf", "playwright_pdf"
    try:
        return _download(url), ".html", "html_snapshot"
    except Exception as error:  # noqa: BLE001
        logger.warning("Webpage snapshot failed for %s: %s", url, error)
        return None, ".html", None


def book_fulltext(isbn: str, *, download: bool = False, out_path: str | None = None) -> dict:
    """Acquire a book PDF by ISBN from Anna's Archive (the books shadow library).

    Resolves the ISBN to an md5 and downloads via the members-only fast tier (if ANNAS_SECRET_KEY is
    set) then the keyless slow tier (which needs a running FlareSolverr at FLARESOLVERR_URL — see
    _solve_challenge). With download=True the PDF is saved (to out_path or a temp file) and its path
    returned, ready to attach to a Zotero book item via zotero_attach. Returns
    {"meta", "isbn", "found", "source", "pdf_path"} — pdf_path is None when no PDF could be obtained.
    """
    data, source = _acquire_book(isbn)
    pdf_path = None
    if data:
        data = validate_pdf(data, origin="book download")
    if data and download:
        target = (pathlib.Path(out_path) if out_path
                  else pathlib.Path(tempfile.gettempdir()) / f"book_{re.sub(r'[^0-9Xx]', '', isbn)}.pdf")
        target.write_bytes(data)
        pdf_path = str(target.resolve())
    return {"meta": {"operation": "book_fulltext"}, "isbn": isbn,
            "found": bool(data), "source": source, "pdf_path": pdf_path}


def webpage_snapshot(url: str, *, out_path: str | None = None) -> dict:
    """Save an artifact for a webpage: a full-page PDF rendered with headless Chromium (Playwright),
    falling back to a raw HTML snapshot only if the browser is unavailable.

    The saved file is suitable for attaching to a Zotero webpage item via zotero_attach. Returns
    {"meta", "url", "found", "source", "path", "content_type"} — path is None when nothing was saved.
    """
    data, ext, source = _acquire_webpage(url)
    path = None
    if data:
        if out_path:
            target = pathlib.Path(out_path)
        else:
            stem = re.sub(r"\W+", "_", url).strip("_")[-60:]
            target = pathlib.Path(tempfile.gettempdir()) / f"snapshot_{stem}{ext}"
        target.write_bytes(data)
        path = str(target.resolve())
    return {"meta": {"operation": "webpage_snapshot"}, "url": url, "found": bool(data),
            "source": source, "path": path, "content_type": "application/pdf" if ext == ".pdf" else "text/html"}


def _extract_figure_images(pdf_bytes: bytes, out_dir: str | None = None) -> tuple[str, list[str]]:
    """Extract the embedded raster figures from a PDF as JPG images, into out_dir or a fresh temp directory.

    JPEG cannot hold alpha or CMYK, so such pixmaps are converted to RGB first.
    """
    workdir = (pathlib.Path(out_dir) if out_dir else pathlib.Path(tempfile.mkdtemp(prefix="scholar_"))).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    image_paths: list[str] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as opened:
        document: Any = opened
        for page_number, page in enumerate(document, start=1):
            for index, image_ref in enumerate(page.get_images(full=True)):
                try:
                    pixmap = fitz.Pixmap(document, image_ref[0])
                    if pixmap.colorspace is None:
                        continue  # An image mask / stencil, not a real figure.
                    if pixmap.alpha or pixmap.n >= 4:
                        pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                    out = workdir / f"page-{page_number:03d}-figure-{index:02d}.jpg"
                    pixmap.save(out, jpg_quality=85)
                    image_paths.append(str(out))
                except Exception as error:  # noqa: BLE001
                    logger.warning("Skipped an embedded image (page %s, #%s): %s", page_number, index, error)
    return str(workdir), image_paths


def _resolve_pdf_bytes(paper_id, pdf_url, pdf_path, email, scihub_proxy) -> tuple[bytes, str]:
    """Obtain (pdf_bytes, source) for the figures function from a local path, a URL, or a paper id."""
    if pdf_path:
        return validate_pdf_file(pdf_path), "local"
    if pdf_url:
        return validate_pdf(_download(pdf_url), origin=pdf_url), "open_access"
    pyalex.config.email = email or None
    _, record = _resolve_work(paper_id)
    resolved_email = email
    pdf_bytes, source = _acquire_pdf(record, _resolve_fulltext_routes(record, resolved_email), scihub_proxy)
    if not pdf_bytes or source is None:
        raise ValueError("No valid PDF could be obtained for this id.")
    return pdf_bytes, source


@batchable("paper_id")
def fulltext(paper_id, *, download=False, out_path=None, out_dir=None, email=None, scihub_proxy=None, source="auto") -> dict:
    """Resolve open-access full-text locations for a paper, and optionally download the PDF.

    Discovers open-access locations and reports them under "routes". With download=True,
    source="auto" tries Sci-Hub first (including .jp), then valid OA PDFs, then Anna routes.
    Choose source="scihub", "open_access", "annas_archive", or "annas_archive_slow"
    to attempt that source only, without fallback. It saves validated PDF bytes and returns their
    "pdf_path" (and the "source" it came from), so the caller can attach it to Zotero and have Claude
    Code read the PDF directly. Choose where it goes: pass out_path for an exact file path, or out_dir
    for a directory (the filename is derived from the id); with neither, a temp directory is used. No
    text is extracted — reading is done by viewing the PDF. The returned "paper" carries the citation
    metadata (title, authors, year, venue, ids).
    """
    if source not in ("auto", "scihub", "open_access", "annas_archive", "annas_archive_slow"):
        raise ValueError(f"Unknown PDF source: {source}")
    _author_email(email)
    _, record = _resolve_work(paper_id)
    resolved_email = email
    routes = _resolve_fulltext_routes(record, resolved_email)

    pdf_path = None
    actual_source = None
    if download:
        pdf_bytes, actual_source = _acquire_pdf(record, routes, scihub_proxy, source=source)
        if pdf_bytes:
            if out_path:
                target = pathlib.Path(out_path)
            else:
                directory = pathlib.Path(out_dir) if out_dir else pathlib.Path(tempfile.mkdtemp(prefix="scholar_"))
                stem = (record["ids"].get("doi") or record["ids"].get("arxiv") or "paper").replace("/", "_")
                target = directory / f"{stem}.pdf"
            target = target.resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(pdf_bytes)
            pdf_path = str(target)

    if download and not pdf_path:
        logger.warning("No valid PDF could be obtained from the requested source(s).")
    elif not routes:
        logger.warning("No open-access full text was located; only the abstract and metadata are available.")
    return {
        "meta": {"operation": "fulltext", "source": actual_source},
        "paper": {"title": record["title"], "authors": record["authors"], "year": record["year"],
                  "venue": record["venue"], "ids": record["ids"], "oa": record.get("oa")},
        "routes": routes,
        "pdf_path": pdf_path,
    }


def _figures_single(*, paper_id=None, pdf_url=None, pdf_path=None, out_dir=None, email=None, scihub_proxy=None) -> dict:
    """Extract the embedded figure images from a paper's PDF as JPG files.

    Provide one source: a paper "paper_id" (resolved to a PDF through the available full-text routes), a direct
    "pdf_url", or a local "pdf_path". Images go to out_dir, or a temp directory when it is omitted; the
    path is returned as "workdir". This pulls the PDF's embedded
    raster images, so vector or composed figures can be missed — to read the whole document (figures in
    context, text, equations), download the PDF with fulltext(..., download=True) and have Claude Code
    read that file directly.
    """
    if not (paper_id or pdf_url or pdf_path):
        raise ValueError("figures requires one of: paper_id, pdf_url, or pdf_path.")
    pdf_bytes, source = _resolve_pdf_bytes(paper_id, pdf_url, pdf_path, email, scihub_proxy)
    workdir, images = _extract_figure_images(pdf_bytes, out_dir)
    return {"meta": {"operation": "figures", "source": source},
            "workdir": workdir, "count": len(images), "images": images}


@functools.wraps(_figures_single)
def figures(*, paper_id=None, pdf_url=None, pdf_path=None, out_dir=None, email=None, scihub_proxy=None):  # noqa: F811
    sources = [("paper_id", paper_id), ("pdf_url", pdf_url), ("pdf_path", pdf_path)]
    listed = next(((name, value) for name, value in sources if isinstance(value, (list, tuple))), None)
    base_kwargs = {"paper_id": paper_id, "pdf_url": pdf_url, "pdf_path": pdf_path,
                   "out_dir": out_dir, "email": email, "scihub_proxy": scihub_proxy}
    if listed is None:
        return _figures_single(**base_kwargs)
    name, values = listed

    def call_one(value):
        try:
            return _figures_single(**{**base_kwargs, name: value})
        except Exception as error:  # noqa: BLE001
            return {"_error": f"{type(error).__name__}: {error}", "input": value}

    return _batch_summary("figures", _parallel_map(call_one, list(values)))
