"""Binary aggregation: mean of log-odds, mild extremizing, optional market blend, then capping."""
import logging
import math

from forecasting_tools import BinaryQuestion

from aleph_bot import config

logger = logging.getLogger(__name__)


def _logit(p: float) -> float:
    """Log-odds of a probability clipped away from 0 and 1."""
    p = min(max(p, 0.001), 0.999)
    return math.log(p / (1 - p))


def aggregate_binary(predictions: list[float], anchor: float | None = None) -> float:
    """LLM logit-mean × EXTREMIZE, blended with a verified market (not extremized), clipped to [CAP, 1-CAP]."""
    mean_logit = sum(_logit(p) for p in predictions) / len(predictions)
    logit = config.EXTREMIZE * mean_logit
    # A judge-verified market is a strong signal (Karger et al.: market alone beat LLMs).
    if anchor is not None:
        logit = config.MARKET_WEIGHT * _logit(anchor) + (1 - config.MARKET_WEIGHT) * logit
    probability = 1 / (1 + math.exp(-logit))
    # Raw inputs and logit BEFORE extremizing: needed later to fit k and the market weight.
    logger.info("aleph_calibration raw=%s mean_logit=%.4f anchor=%s final=%.4f",
                [round(p, 4) for p in predictions], mean_logit, anchor, probability)
    return min(max(probability, config.CAP), 1 - config.CAP)


class CalibrationMixin:
    """Replaces the median for binary questions; other types keep the parent aggregation."""

    async def _aggregate_predictions(self, predictions, question):
        """Calibrated logit-mean (+ market anchor) for binary questions, parent behaviour otherwise."""
        # Binary: our aggregation; numeric/MC/date/conditional: framework median.
        if isinstance(question, BinaryQuestion):
            anchor = getattr(self, "anchors", {}).get(question.page_url)
            return aggregate_binary(predictions, anchor)
        return await super()._aggregate_predictions(predictions, question)
