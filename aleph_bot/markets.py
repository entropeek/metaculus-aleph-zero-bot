"""Free prediction-market lookup (Manifold, Polymarket): research text and anchor candidates."""
import asyncio
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from aleph_bot import config

STOPWORDS = set("will the a an of in on by to be is at for before after than or and with what how many".split())


def _keywords(text: str, limit: int = 6) -> str:
    """Keeps the first meaningful words of the question for the search."""
    words = [w for w in re.findall(r"[A-Za-z0-9$%.]+", text) if w.lower() not in STOPWORDS]
    return " ".join(words[:limit])


def _get_json(url: str) -> object:
    """Downloads and decodes a JSON document with a short timeout."""
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)


def _market(source: str, question: str, prob: float, volume: float, end: str) -> dict:
    """Uniform market record; 'liquid' marks markets usable as an anchor."""
    return {"source": source, "question": question, "prob": prob, "volume": volume,
            "end": (end or "?")[:10], "liquid": volume >= config.MIN_VOLUME[source]}


def _manifold(term: str) -> list[dict]:
    """Returns open Manifold binary markets matching the term."""
    url = "https://api.manifold.markets/v0/search-markets?" + urllib.parse.urlencode(
        {"term": term, "limit": 4, "filter": "open", "contractType": "BINARY"}
    )
    return [_market("Manifold", m["question"], m["probability"], m.get("volume", 0), _ms_to_date(m.get("closeTime")))
            for m in _get_json(url)]


def _ms_to_date(ms: int | None) -> str:
    """Converts a Manifold closeTime (ms since epoch) to YYYY-MM-DD; empty when missing."""
    return datetime.fromtimestamp(ms / 1000, timezone.utc).date().isoformat() if ms else ""


def _polymarket(term: str) -> list[dict]:
    """Returns open Polymarket markets matching the term (Yes price = first outcomePrices entry)."""
    url = "https://gamma-api.polymarket.com/public-search?" + urllib.parse.urlencode(
        {"q": term, "limit_per_type": 3}
    )
    events = _get_json(url).get("events", [])
    markets = [m for e in events for m in e.get("markets", []) if not m.get("closed")]
    return [_market("Polymarket", m["question"], float(json.loads(m["outcomePrices"])[0]),
                    float(m.get("volumeNum") or 0), m.get("endDate", "")) for m in markets[:4]]


def find_markets(question_text: str) -> list[dict]:
    """Collects markets from every source; a failing source is skipped, never fatal."""
    term, markets = _keywords(question_text), []
    for source in (_manifold, _polymarket):
        try:
            markets += source(term)
        except Exception:  # Network or format error: ignore this source.
            continue
    return markets


def render(markets: list[dict]) -> str:
    """Research text listing the markets, with an explicit mismatch warning."""
    header = "Possibly related prediction markets (may NOT match the exact question or criteria; use only as a weak anchor):"
    lines = [f"- {m['source']}: {m['question']} -> {m['prob']:.0%} (volume {m['volume']:.0f}, ends {m['end']})"
             for m in markets]
    return "\n".join([header, *lines]) if lines else ""


async def market_search(question_text: str) -> list[dict]:
    """Async wrapper so the lookup does not block the event loop."""
    return await asyncio.to_thread(find_markets, question_text)
