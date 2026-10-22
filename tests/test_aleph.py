"""Offline unit tests for Aleph Zero calibration, market anchor and market parsing."""
import asyncio
import math

from forecasting_tools import BinaryQuestion

from aleph_bot import anchor, calibration, config, markets

QUESTION = BinaryQuestion(question_text="Will X happen by 2026-12-31?", resolution_criteria="X per source",
                          scheduled_resolution_time="2026-12-31", page_url="u1")
MARKETS = [{"source": "Polymarket", "question": "Will X happen by Dec 31?", "prob": 0.8,
            "volume": 50000.0, "end": "2026-12-31", "liquid": True}]


def test_aggregate_neutral_and_symmetric():
    """50% stays 50%; mirrored inputs give mirrored outputs."""
    assert calibration.aggregate_binary([0.5, 0.5, 0.5]) == 0.5
    high, low = calibration.aggregate_binary([0.7, 0.8]), calibration.aggregate_binary([0.3, 0.2])
    assert math.isclose(high, 1 - low)


def test_aggregate_extremizes_and_caps():
    """Agreeing forecasts move away from 50%; extremes are capped."""
    assert calibration.aggregate_binary([0.7, 0.7, 0.7]) > 0.7
    assert calibration.aggregate_binary([0.999, 0.999]) == 1 - config.CAP
    assert calibration.aggregate_binary([0.0, 0.001]) == config.CAP


def test_anchor_pulls_toward_market():
    """A verified market moves the result toward its price, by MARKET_WEIGHT in log-odds."""
    alone, blended = calibration.aggregate_binary([0.4, 0.4]), calibration.aggregate_binary([0.4, 0.4], 0.8)
    assert alone < blended < 0.8


def test_parse_verdict():
    """The price comes from the data; invalid or missing choices give None."""
    assert anchor.parse_verdict("reasoning...\nMATCH: 1", MARKETS) == 0.8
    assert anchor.parse_verdict("MATCH: 3", MARKETS) is None
    assert anchor.parse_verdict("NONE", MARKETS) is None
    assert anchor.parse_verdict(None, MARKETS) is None


class _Llm:
    """Fake judge model returning a fixed answer, or raising."""

    def __init__(self, answer):
        self.answer, self.calls = answer, 0

    async def invoke(self, prompt):
        """Returns the canned answer (raises if it is an exception)."""
        self.calls += 1
        # Simulate an API failure.
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


def test_judge_paths():
    """Match, failure and empty candidate list (no LLM call)."""
    assert asyncio.run(anchor.judge(_Llm("MATCH: 1"), QUESTION, MARKETS)) == 0.8
    assert asyncio.run(anchor.judge(_Llm(RuntimeError("down")), QUESTION, MARKETS)) is None
    idle = _Llm("MATCH: 1")
    assert asyncio.run(anchor.judge(idle, QUESTION, [])) is None and idle.calls == 0


def test_market_records_and_failures(monkeypatch):
    """Polymarket parsing, liquidity flag, and a failing source never breaks the lookup."""
    event = {"events": [{"markets": [
        {"question": "Q?", "outcomePrices": '["0.3", "0.7"]', "volumeNum": 30000, "endDate": "2026-12-01T00:00Z"},
        {"question": "Old?", "outcomePrices": '["1", "0"]', "closed": True}]}]}

    def fake_get(url):
        """Manifold fails, Polymarket returns the event above."""
        # Only the Polymarket host answers.
        if "manifold" in url:
            raise OSError("offline")
        return event
    monkeypatch.setattr(markets, "_get_json", fake_get)
    found = markets.find_markets("Will Q happen?")
    assert found == [{"source": "Polymarket", "question": "Q?", "prob": 0.3, "volume": 30000.0,
                      "end": "2026-12-01", "liquid": True}]
    assert "Q? -> 30%" in markets.render(found) and markets.render([]) == ""
