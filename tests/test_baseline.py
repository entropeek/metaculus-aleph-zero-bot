"""Offline tests for the random-walk numeric baseline."""
from datetime import date, timedelta

from aleph_bot import baseline


def test_fred_ids():
    """Series ids are taken from FRED series URLs, deduplicated."""
    text = "per https://fred.stlouisfed.org/series/DGS10 and fred.stlouisfed.org/series/DGS10, see also FRED"
    assert baseline.fred_ids(text) == ["DGS10"]


def test_quantiles_monotone_and_centered():
    """Quantiles increase; a symmetric walk is centered on the last value."""
    values = [100 + (1 if i % 2 else -1) for i in range(500)] + [100]
    quantiles = list(baseline.random_walk_quantiles(values, 1).values())
    assert quantiles == sorted(quantiles)
    assert abs(baseline.random_walk_quantiles(values, 2)[0.5] - 100) < 1e-9


def test_negative_series_uses_differences():
    """Series with non-positive values use additive changes."""
    values = [(-1) ** i * 0.5 for i in range(300)]
    assert baseline.random_walk_quantiles(values, 2)[0.5] == values[-1]


def test_steps_until_daily_and_monthly():
    """Horizon in observations from the series spacing."""
    daily = [(date(2026, 1, 1) + timedelta(days=i), 1.0) for i in range(100)]
    assert baseline.steps_until(daily, daily[-1][0] + timedelta(days=10)) == 10
    monthly = [(date(2020 + i // 12, i % 12 + 1, 1), 1.0) for i in range(80)]
    assert baseline.steps_until(monthly, date(2026, 12, 1)) == 4  # last obs 2026-08-01


def test_baseline_text_offline(monkeypatch):
    """No link or a failing download gives an empty paragraph."""
    assert baseline.baseline_text("no series here", date(2026, 12, 1)) == ""
    monkeypatch.setattr(baseline, "load_fred", lambda sid: (_ for _ in ()).throw(OSError("offline")))
    assert baseline.baseline_text("fred.stlouisfed.org/series/DGS10", date(2026, 12, 1)) == ""
