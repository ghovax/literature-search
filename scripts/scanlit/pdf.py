"""PDF sources, explicit route selection, acquisition, and validation.

Default order: Sci-Hub, open-access locations, Anna member route, Anna slow route.
Only validated PDF bytes may leave this module as an acquired PDF.
"""
import os
import pathlib
import pymupdf
import re
import urllib.parse
from typing import Any
import httpx
from .common import REQUEST_TIMEOUT, _http_get, _load_dotenv, logger


def _resolve_fulltext_routes(record: dict, email: str) -> list[dict]:
    """Collect every legal open-access full-text location available for a record."""
    identifiers = record["ids"]
    routes: list[dict] = []
    if identifiers.get("arxiv"):
        routes.append({"route": "arxiv", "pdf_url": f"https://arxiv.org/pdf/{identifiers['arxiv']}"})
    pmcid = identifiers.get("pmcid")
    if not pmcid and identifiers.get("doi"):  # OpenAlex sometimes lacks the PMCID; ask Europe PMC by DOI.
        try:
            search = _http_get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                               {"query": f"DOI:{identifiers['doi']}", "format": "json", "pageSize": 1}).json()
            hit = (search.get("resultList", {}).get("result") or [None])[0]
            if hit and hit.get("pmcid"):
                pmcid = hit["pmcid"]
        except Exception as error:  # noqa: BLE001
            logger.warning("Europe PMC PMCID lookup failed: %s", error)
    if pmcid:
        pmcid = pmcid if str(pmcid).upper().startswith("PMC") else f"PMC{pmcid}"
        routes.append({"route": "europepmc",
                       "xml_url": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"})
    if (record.get("oa") or {}).get("pdf_url"):
        routes.append({"route": "openalex_oa", "pdf_url": record["oa"]["pdf_url"]})
    doi = identifiers.get("doi")
    if doi:
        try:
            unpaywall: Any = _http_get(f"https://api.unpaywall.org/v2/{doi}", {"email": email}).json()
            best = unpaywall.get("best_oa_location") or {}
            if best.get("url_for_pdf"):
                routes.append({"route": "unpaywall", "pdf_url": best["url_for_pdf"]})
        except Exception as error:  # noqa: BLE001
            logger.warning("Unpaywall lookup failed: %s", error)
    if doi and doi.startswith("10.1101"):  # bioRxiv / medRxiv preprint DOIs
        for server in ("biorxiv", "medrxiv"):
            try:
                detail: Any = _http_get(f"https://api.biorxiv.org/details/{server}/{doi}").json()
                collection = detail.get("collection") or []
                if collection and collection[-1].get("jatsxml"):
                    routes.append({"route": server, "xml_url": collection[-1]["jatsxml"]})
                    break
            except Exception as error:  # noqa: BLE001
                logger.warning("%s lookup failed: %s", server, error)
    if doi:
        try:
            headers = {"Authorization": f"Bearer {os.environ['CORE_API_KEY']}"} if os.environ.get("CORE_API_KEY") else {}
            with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
                core: Any = client.get("https://api.core.ac.uk/v3/search/works/",
                                       params={"q": f'doi:"{doi}"', "limit": 1}).json()
            hits = core.get("results") or []
            if hits and hits[0].get("downloadUrl"):
                routes.append({"route": "core", "pdf_url": hits[0]["downloadUrl"]})
        except Exception as error:  # noqa: BLE001
            logger.warning("CORE lookup failed: %s", error)
    return routes


def _download(url: str) -> bytes:
    """Download a URL's raw bytes (used for PDFs)."""
    response = _http_get(url)
    response.raise_for_status()
    return response.content


# Ordered fallback mirrors; availability is network- and time-dependent.
SCIHUB_MIRRORS = [
    "https://sci-hub.jp",
    "https://sci-hub.st",
    "https://sci-hub.ru",
    "https://sci-hub.box",
    "https://sci-hub.red",
    "https://sci-hub.shop",
    "https://sci-hub.al",
    "https://sci-hub.ren",
    "https://sci-hub.mksa.top",
    "https://www.wellesu.com",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
    "https://sci-hub.org",
    "https://sci-hub.now.sh",
    "https://sci-hub.41610.org",
    "https://sci.bban.top",
    "https://sci-hub.usualwant.com",
    "https://sci-hub.hkvisa.net",
    "https://sci-hub.scihubtw.tw",
    "https://sci-hub.cat",
    "https://sci-hub.do",
    "https://sci-hub.unblockit.id",
    "https://sci-hub.se",
    "https://sci-hub.te",
]
_BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _scihub_pdf_url(html: str) -> str | None:
    """Find the PDF link on a Sci-Hub article page (the citation_pdf_url meta, or an embed/iframe/object)."""
    patterns = [
        r'name="citation_pdf_url"\s+content="([^"]+)"',
        r'<embed[^>]+src="([^"]+\.pdf[^"]*)"',
        r'<iframe[^>]+src="([^"]+\.pdf[^"]*)"',
        r'<object[^>]+data="([^"]+\.pdf[^"]*)"',
        r"location\.href='([^']+\.pdf[^']*)'",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return match.group(1)
    return None


def _scihub_pdf(doi: str, scihub_proxy: str | None) -> bytes:
    """Fetch a paper PDF by DOI from a Sci-Hub mirror as a fallback route.

    Sci-Hub sits behind DDoS-Guard and serves the PDF link in the page (a citation_pdf_url meta tag or
    an embed element), on mirrors that sometimes present invalid certificates. This parses the article
    page and downloads the PDF directly, trying each mirror in turn. Certificate verification is disabled
    because the mirrors require it, and scihub_proxy (an httpx proxy URL such as "socks5://127.0.0.1:7890")
    is used when provided.
    """
    client_arguments: dict[str, Any] = {"headers": {"User-Agent": _BROWSER_UA}, "follow_redirects": True,
                                        "timeout": REQUEST_TIMEOUT, "verify": False}
    if scihub_proxy:
        client_arguments["proxy"] = scihub_proxy
    last_error: Any = None
    for mirror in SCIHUB_MIRRORS:
        try:
            with httpx.Client(**client_arguments) as client:
                pdf_url = _scihub_pdf_url(client.get(f"{mirror}/{doi}").text)
                if not pdf_url:
                    continue
                pdf_url = pdf_url.split("#")[0]
                if pdf_url.startswith("//"):
                    pdf_url = "https:" + pdf_url
                elif pdf_url.startswith("/"):
                    pdf_url = mirror + pdf_url
                response = client.get(pdf_url)
                if response.status_code == 200:
                    try:
                        return validate_pdf(response.content, origin=f"Sci-Hub {mirror}")
                    except ValueError as error:
                        logger.warning("Sci-Hub mirror %s returned invalid PDF: %s", mirror, error)
        except Exception as error:  # noqa: BLE001
            last_error = error
            logger.warning("Sci-Hub mirror %s failed: %s", mirror, error)
    raise RuntimeError(f"Sci-Hub returned no PDF for {doi} ({last_error})")


# Anna's Archive official member API fallback. Covers papers newer than Sci-Hub's 2021 freeze.
# DORMANT unless ANNAS_SECRET_KEY (an active *paid* membership secret key) is present in the
# environment or a project .env — without it this returns None and changes nothing. Only the
# members-only fast-download JSON API is automatable: the free "slow" tier and the .li/.org/.se
# web frontends sit behind a JS anti-bot wall (DDoS-Guard) that a plain HTTP client cannot pass.
# These three official mirror domains served the API and the md5 pages challenge-free when probed
# (2026-06-08); they rotate, so cross-check against Anna's Wikipedia page if all three fail.


ANNAS_DOMAINS = ["https://annas-archive.gl", "https://annas-archive.pk", "https://annas-archive.gd"]
ANNAS_SLOW_SERVERS = 5  # partner-server slots tried per md5 on the keyless slow-download tier


def _annas_resolve_md5(doi: str, client: httpx.Client) -> str | None:
    """Resolve a DOI to its Anna's Archive md5 via the canonical SciDB record page.

    `/scidb/<doi>` redirects to the single canonical record (one md5, resolved by Anna itself) when
    the paper is in SciDB, or to the fuzzy `/search?...` page when it is not. Only the record page is
    trusted — a redirect to search means "no SciDB record" and returns None rather than guessing
    from a similarly-named paper. Pages are fetched through _solve_challenge, so resolution survives a
    JS wall on the record page when FLARESOLVERR_URL is configured.
    """
    for domain in ANNAS_DOMAINS:
        html, _ = _solve_challenge(f"{domain}/scidb/{urllib.parse.quote(doi)}", client)
        if not html or re.search(r"<title>[^<]*- Search - Anna", html):
            continue  # no canonical record (fuzzy search fallback), or still challenged
        match = re.search(r"/md5/([0-9a-f]{32})", html)
        if match:
            return match.group(1)
    return None


def _annas_client_args(scihub_proxy: str | None) -> dict:
    """Shared httpx.Client kwargs for Anna's Archive (browser UA, redirects, optional proxy)."""
    args: dict[str, Any] = {"headers": {"User-Agent": _BROWSER_UA}, "follow_redirects": True,
                            "timeout": REQUEST_TIMEOUT, "verify": False}
    if scihub_proxy:
        args["proxy"] = scihub_proxy
    return args


def _annas_fast_download_md5(md5: str, key: str, client: httpx.Client) -> bytes | None:
    """Download a file by md5 via Anna's members-only fast-download JSON API (needs a paid key)."""
    for domain in ANNAS_DOMAINS:
        try:
            response = client.get(f"{domain}/dyn/api/fast_download.json", params={"md5": md5, "key": key})
            payload = response.json()
        except Exception as error:  # noqa: BLE001
            logger.warning("Anna's Archive API on %s failed: %s", domain, error)
            continue
        download_url = payload.get("download_url")
        if not download_url:
            logger.warning("Anna's Archive API error for md5 %s: %s", md5, payload.get("error"))
            if response.status_code in (401, 403):
                break  # an auth/membership error is the same on every mirror; stop early
            continue
        try:
            return validate_pdf(client.get(download_url).content, origin="Anna member download")
        except ValueError:
            pass
        logger.warning("Anna's Archive download_url did not return a PDF for md5 %s", md5)
    return None


def _annas_pdf(doi: str, scihub_proxy: str | None) -> bytes | None:
    """Fetch a paper PDF by DOI from Anna's Archive's member API, or None if unavailable.

    Returns None (silently dormant) when no ANNAS_SECRET_KEY is configured. With a key: resolve the
    DOI to an md5, then download via the members-only fast-download API.
    """
    _load_dotenv()
    key = os.environ.get("ANNAS_SECRET_KEY")
    if not key:
        return None
    with httpx.Client(**_annas_client_args(scihub_proxy)) as client:
        md5 = _annas_resolve_md5(doi, client)
        if not md5:
            logger.warning("Anna's Archive: no exact md5 match for %s", doi)
            return None
        return _annas_fast_download_md5(md5, key, client)


def _solve_challenge(url: str, client: httpx.Client) -> tuple[str | None, dict[str, str]]:
    """Fetch a URL, transparently passing any DDoS-Guard / Cloudflare browser challenge.

    Returns (html, cookies). A plain GET is tried first; if it is blocked by a JS anti-bot wall and
    a FLARESOLVERR_URL is configured (a running FlareSolverr instance, which solves DDoS-Guard), the
    request is routed through it and the solved HTML + cookies are returned. Without a solver a
    challenged page yields (None, {}) — the caller treats that as "unavailable" rather than failing.
    """
    try:
        response = client.get(url)
        if "DDoS-Guard" not in response.text and "Checking your browser" not in response.text:
            return response.text, {}
    except Exception as error:  # noqa: BLE001
        logger.warning("GET %s failed: %s", url, error)
    _load_dotenv()
    solver = os.environ.get("FLARESOLVERR_URL")
    if not solver:
        logger.warning("%s is behind a browser challenge; set FLARESOLVERR_URL to bypass it.", url)
        return None, {}
    try:
        # FlareSolverr drives a real browser, so the POST must outlast its own solve budget
        # (maxTimeout) — the default 30s client timeout would abort mid-solve.
        solve_ms = 60000
        solved = client.post(f"{solver.rstrip('/')}/v1",
                             json={"cmd": "request.get", "url": url, "maxTimeout": solve_ms},
                             timeout=httpx.Timeout(solve_ms / 1000 + 15)).json()
        solution = solved.get("solution") or {}
        cookies = {cookie["name"]: cookie["value"] for cookie in solution.get("cookies", []) if "name" in cookie}
        return solution.get("response"), cookies
    except Exception as error:  # noqa: BLE001
        logger.warning("FlareSolverr could not solve %s: %s", url, error)
        return None, {}


def _annas_slow_download_md5(md5: str, client: httpx.Client) -> bytes | None:
    """Download a file by md5 via Anna's keyless "slow download" tier (behind DDoS-Guard).

    Needs no membership key, but the slow endpoints sit behind a browser challenge, so a PDF comes
    back only on a network/domain where the wall is down or when FLARESOLVERR_URL is set (see
    _solve_challenge). Each md5 is offered by several partner servers (/slow_download/<md5>/0/N); the
    waitlist page is parsed for the final external file link, which is then downloaded.
    """
    for domain in ANNAS_DOMAINS:
        for server_index in range(ANNAS_SLOW_SERVERS):
            page_url = f"{domain}/slow_download/{md5}/0/{server_index}"
            html, cookies = _solve_challenge(page_url, client)
            if not html:
                continue
            # The page links the file on an external partner server (an absolute http(s) URL
            # ending in .pdf, off the annas-archive domain) — match that, not the internal
            # /md5/ record links (which also contain the md5) or the donation anchors.
            patterns = (r'href="(https?://(?!annas-archive)[^"]+\.pdf[^"]*)"',
                        r'href="(https?://(?!annas-archive)[^"]+/d/[^"]+)"')
            link = next((match.group(1) for pattern in patterns
                         for match in [re.search(pattern, html, re.I)] if match), None)
            if not link:
                continue
            if link.startswith("/"):
                link = domain + link
            try:
                data = client.get(link, cookies=cookies).content
            except Exception as error:  # noqa: BLE001
                logger.warning("Anna's Archive (slow) link fetch failed for md5 %s: %s", md5, error)
                continue
            try:
                return validate_pdf(data, origin="Anna slow download")
            except ValueError:
                continue
    return None


def _annas_slow_pdf(doi: str, scihub_proxy: str | None) -> bytes | None:
    """Fetch a paper PDF by DOI via Anna's keyless slow tier (needs FlareSolverr; see _solve_challenge)."""
    with httpx.Client(**_annas_client_args(scihub_proxy)) as client:
        md5 = _annas_resolve_md5(doi, client)
        if not md5:
            logger.warning("Anna's Archive (slow): no exact md5 match for %s", doi)
            return None
        return _annas_slow_download_md5(md5, client)


def _annas_md5_from_isbn(isbn: str, client: httpx.Client) -> str | None:
    """Resolve an ISBN to an Anna's Archive md5 via its search page (top result).

    Books have no DOI/SciDB record, so resolution is by ISBN search rather than the canonical /scidb
    path used for papers; the first /md5/ link on the results page is the top-ranked match. Fetched
    through _solve_challenge so it survives the DDoS-Guard wall when FLARESOLVERR_URL is set.
    """
    clean = re.sub(r"[^0-9Xx]", "", isbn)
    for domain in ANNAS_DOMAINS:
        html, _ = _solve_challenge(f"{domain}/search?q={urllib.parse.quote(clean)}", client)
        if not html:
            continue
        match = re.search(r"/md5/([0-9a-f]{32})", html)
        if match:
            return match.group(1)
    logger.warning("Anna's Archive: no md5 match for ISBN %s", isbn)
    return None


def _acquire_book(isbn: str, scihub_proxy: str | None = None) -> tuple[bytes | None, str | None]:
    """Return (pdf_bytes, source) for a book by ISBN from Anna's Archive: the members-only fast tier
    if ANNAS_SECRET_KEY is set, then the keyless slow tier. Books are a shadow-library strength,
    unlike post-2021 journal papers, so this is the realistic way to acquire a textbook PDF."""
    _load_dotenv()
    with httpx.Client(**_annas_client_args(scihub_proxy)) as client:
        md5 = _annas_md5_from_isbn(isbn, client)
        if not md5:
            return None, None
        key = os.environ.get("ANNAS_SECRET_KEY")
        if key and (data := _annas_fast_download_md5(md5, key, client)):
            return data, "annas_archive"
        if data := _annas_slow_download_md5(md5, client):
            return data, "annas_archive_slow"
    return None, None


PDF_SOURCES = ("scihub", "open_access", "annas_archive", "annas_archive_slow")


def _acquire_pdf(record: dict, routes: list[dict], scihub_proxy: str | None = None,
                 *, source: str = "auto") -> tuple[bytes | None, str | None]:
    """Try a chosen source or ordered fallbacks, returning only validated PDF bytes.

    With source='auto', tries Sci-Hub first (including .jp), then all OA PDF URLs,
    then Anna's member and slow routes. With a named source only that route is tried.
    No implicit fallback occurs when a specific source is requested.
    """
    if source != "auto" and source not in PDF_SOURCES:
        raise ValueError(f"Unknown PDF source {source!r}; choose 'auto' or {PDF_SOURCES}")
    doi = (record.get("ids") or {}).get("doi")
    sources = PDF_SOURCES if source == "auto" else (source,)
    for chosen in sources:  # ordered fallbacks: stop immediately on a valid result
        if chosen == "open_access":
            for route in routes:  # ordered OA locations can fail independently
                url = route.get("pdf_url")
                if not url:
                    continue
                try:
                    return validate_pdf(_download(url), origin=url), "open_access"
                except Exception as error:  # noqa: BLE001
                    logger.warning("Open-access PDF location %s failed: %s", url, error)
            continue
        if not doi:
            continue
        fetch = {"scihub": _scihub_pdf, "annas_archive": _annas_pdf,
                 "annas_archive_slow": _annas_slow_pdf}[chosen]
        try:
            data = fetch(doi, scihub_proxy)
            if data:
                return validate_pdf(data, origin=chosen), chosen
        except Exception as error:  # noqa: BLE001
            logger.warning("%s fetch failed for %s: %s", chosen, doi, error)
    return None, None


def validate_pdf(data: bytes, *, origin: str = "PDF") -> bytes:
    """Return bytes only if they contain a readable, nonempty PDF; raise ValueError otherwise."""
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"{origin}: not a PDF (missing %PDF- signature; possibly HTML)")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as document:
            if document.is_encrypted or document.page_count < 1:
                raise ValueError(f"{origin}: encrypted or empty PDF")
            # Exercise the parser, not just the header check.
            document.load_page(0)
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"{origin}: unreadable PDF: {error}") from error
    return data


def validate_pdf_file(path: str | pathlib.Path) -> bytes:
    """Validate a local PDF before creating a Zotero attachment or uploading bytes."""
    return validate_pdf(pathlib.Path(path).read_bytes(), origin=str(path))

def pdf_check(pdf_path: str | pathlib.Path) -> dict:
    """Inspect a local file without uploading it; report validity and page count."""
    path = pathlib.Path(pdf_path)
    try:
        data = validate_pdf_file(path)
        with pymupdf.open(stream=data, filetype="pdf") as document:
            pages = document.page_count
        return {"path": str(path), "valid": True, "pages": pages, "bytes": len(data), "error": None}
    except (OSError, ValueError) as error:
        return {"path": str(path), "valid": False, "pages": 0,
                "bytes": path.stat().st_size if path.exists() else 0,
                "error": f"{type(error).__name__}: {error}"}
