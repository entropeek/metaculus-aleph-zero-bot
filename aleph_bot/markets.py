"""Free prediction-market lookup (Manifold, Polymarket) used as a research anchor."""
import asyncio
import json
import re
import urllib.parse
import urllib.request

STOPWORDS = set("will the a an of in on by to be is at for before after than or and with what how many".split())


def _keywords(text: str, limit: int = 6) -> str:
    """Keeps the first meaningful words of the question for the search."""
    words = [w for w in re.findall(r"[A-Za-z0-9$%.]+", text) if w.lower() not in STOPWORDS]
    return " ".join(words[:limit])


def _get_json(url: str) -> object:
    """Downloads and decodes a JSON document with a short timeout."""
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def _manifold(term: str) -> list[str]:
    """Returns open Manifold binary markets matching the term."""
    url = "https://api.manifold.markets/v0/search-markets?" + urllib.parse.urlencode(
        {"term": term, "limit": 4, "filter": "open", "contractType": "BINARY"}
    )
    # One line per market: question, probability, volume.
    return [
        f"- Manifold: {m['question']} -> {m['probability']:.0%} (volume {m.get('volume', 0):.0f})"
        for m in _get_json(url)
    ]


def _polymarket(term: str) -> list[str]:
    """Returns open Polymarket markets matching the term."""
    url = "https://gamma-api.polymarket.com/public-search?" + urllib.parse.urlencode(
        {"q": term, "limit_per_type": 3}
    )
    events = _get_json(url).get("events", [])
    markets = [m for e in events for m in e.get("markets", []) if not m.get("closed")]
    # Price of the "Yes" outcome is the first entry of outcomePrices.
    return [
        f"- Polymarket: {m['question']} -> {float(json.loads(m['outcomePrices'])[0]):.0%}"
        for m in markets[:4]
    ]


def _lookup(question_text: str) -> str:
    """Collects market lines; a failing source is skipped, never fatal."""
    term, lines = _keywords(question_text), []
    for source in (_manifold, _polymarket):
        try:
            lines += source(term)
        except Exception:  # Network or format error: ignore this source.
            continue
    header = "Possibly related prediction markets (may NOT match the exact question or criteria; use only as a weak anchor):"
    return "\n".join([header, *lines]) if lines else ""


async def market_context(question_text: str) -> str:
    """Async wrapper so the lookup does not block the event loop."""
    return await asyncio.to_thread(_lookup, question_text)
