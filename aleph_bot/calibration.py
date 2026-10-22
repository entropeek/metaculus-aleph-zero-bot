"""Binary aggregation: mean of log-odds, mild extremizing, then capping (LLMs hedge toward 50%)."""
import math

from forecasting_tools import BinaryQuestion

from aleph_bot import config


def aggregate_binary(predictions: list[float]) -> float:
    """Logit-mean of the ensemble, pushed away from 50% by EXTREMIZE, clipped to [CAP, 1-CAP]."""
    clipped = [min(max(p, 0.001), 0.999) for p in predictions]
    mean_logit = sum(math.log(p / (1 - p)) for p in clipped) / len(clipped)
    probability = 1 / (1 + math.exp(-config.EXTREMIZE * mean_logit))
    return min(max(probability, config.CAP), 1 - config.CAP)


class CalibrationMixin:
    """Replaces the median for binary questions; other types keep the parent aggregation."""

    async def _aggregate_predictions(self, predictions, question):
        """Calibrated logit-mean for binary questions, parent behaviour otherwise."""
        # Binary: our aggregation; numeric/MC/date: framework median.
        if isinstance(question, BinaryQuestion):
            return aggregate_binary(predictions)
        return await super()._aggregate_predictions(predictions, question)
