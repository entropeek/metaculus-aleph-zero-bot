"""Reads the pages named in a question's resolution criteria (free, failure-tolerant)."""
import asyncio
import html
import re
import urllib.request

MAX_PAGES, MAX_CHARS = 2, 3500
URL_PATTERN = re.compile(r"https?://[^\s)\]>\"']+")


def _page_text(url: str) -> str:
    """Downloads a page and returns its visible text, truncated."""
    request = urllib.request.Request(url, headers={"User-Agent": "AlephZeroBot/1.0 (forecasting)"})
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read(400_000).decode("utf-8", errors="ignore")
    # Keep the main content when the page marks it (skips menus).
    main = re.search(r"(?is)<(main|article)[^>]*>(.*)</\1>", raw)
    raw = main.group(2) if main else raw
    # Drop scripts/styles, then tags, then collapse whitespace.
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()
    return text[:MAX_CHARS]


def _read_sources(criteria: str) -> str:
    """Reads the first resolution-source URLs; unreadable pages are skipped."""
    urls = list(dict.fromkeys(u.rstrip(".,;") for u in URL_PATTERN.findall(criteria)))
    blocks = []
    for url in urls[:MAX_PAGES]:
        try:
            text = _page_text(url)
        except Exception:  # Blocked, PDF, timeout: skip this page.
            continue
        # Pages that are mostly empty (JavaScript apps) are worse than nothing.
        if len(text) > 300:
            blocks.append(f"[{url}] (raw extract, may be partial or outdated)\n{text}")
    header = "Resolution source pages:"
    return "\n\n".join([header, *blocks]) if blocks else ""


async def source_context(criteria: str) -> str:
    """Async wrapper so page reads do not block the event loop."""
    return await asyncio.to_thread(_read_sources, criteria)
