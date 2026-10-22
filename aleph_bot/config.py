"""Aleph Zero bot settings, all overridable through environment variables."""
import os

# Forecasting models (2-3 families), cycled across forecasts (comma-separated litellm names).
MODELS = os.getenv(
    "ALEPH_MODELS",
    # ~$0.09/question per forecast round (3 calls) at 2026-10-22 OpenRouter prices; Google avoided (shared 150 rpm limit).
    "openrouter/anthropic/claude-sonnet-5.5,openrouter/openai/gpt-6.1-sol,openrouter/deepseek/deepseek-v4-pro",
).split(",")
# Reasoning effort for the ensemble (low/medium/high); "high" ~doubles the cost per question.
REASONING_EFFORT = os.getenv("ALEPH_REASONING", "medium")
# Forecasts per model and question (AIA: big gains from 1 to 5 samples total); 2 ~ $0.18/question.
SAMPLES_PER_MODEL = int(os.getenv("ALEPH_SAMPLES", "2"))
# Binary calibration: log-odds slope k (1 = none). 1.1 until fitted on resolved questions:
# over-extremizing costs more than under-extremizing (report "Méthode pour gagner FutureEval").
EXTREMIZE = float(os.getenv("ALEPH_EXTREMIZE", "1.1"))
# Probability floor/ceiling, applied after extremizing.
CAP = float(os.getenv("ALEPH_CAP", "0.02"))
# Cheap model that extracts the number from each model's reasoning.
PARSER = os.getenv("ALEPH_PARSER", "openrouter/openai/gpt-6-luna")
# Free for participants: AskNews news summaries.
RESEARCHER = os.getenv("ALEPH_RESEARCHER", "asknews/news-summaries")
# Hard spending cap per run, in USD (one run every 20 minutes).
MAX_COST_PER_RUN = float(os.getenv("ALEPH_MAX_COST_PER_RUN", "3.0"))
# Free prediction-market lookup (Manifold, Polymarket) added to the research.
USE_MARKETS = os.getenv("ALEPH_USE_MARKETS", "true").lower() == "true"
# Public signature added to every published comment (AI transparency).
SIGNATURE = (
    "Forecast by Aleph Zero, an AI agent running on Claude (Anthropic), "
    "operated under human supervision. Open-source code."
)
# Cheaper fallback ensemble (~$0.02/question) if credits run low:
# claude-haiku-5.5, gpt-5.6-luna, deepseek-v4-flash (prefix "openrouter/").
