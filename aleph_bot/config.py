"""Aleph Zero bot settings, all overridable through environment variables."""
import os

# Forecasting models (2-3 families), cycled across forecasts (comma-separated litellm names).
MODELS = os.getenv(
    "ALEPH_MODELS",
    # Metaculus credits cover only OpenAI, Anthropic and Google (resources page, 2026-10-22).
    # Google shares a ~150 rpm limit: fine at 1 call per question per model.
    "openrouter/anthropic/claude-sonnet-5.5,openrouter/openai/gpt-6.1-sol,openrouter/google/gemini-4-argon",
).split(",")
# Reasoning effort for the ensemble (low/medium/high); "high" ~doubles the cost per question.
REASONING_EFFORT = os.getenv("ALEPH_REASONING", "medium")
# Forecasts per model and question. 1 keeps ~600 questions within ~$100 of credits (running out = 0 points);
# raise to 2 (~$0.18/question) only if more credits are granted.
SAMPLES_PER_MODEL = int(os.getenv("ALEPH_SAMPLES", "1"))
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
# Weight of a judge-verified, liquid market in the binary log-odds blend (AIA: LLM ~1/3 of the optimal weight).
MARKET_WEIGHT = float(os.getenv("ALEPH_MARKET_WEIGHT", "0.5"))
# Minimum traded volume for a market to be used as an anchor (Manifold: play money; Polymarket: USD).
MIN_VOLUME = {"Manifold": 5000.0, "Polymarket": 20000.0}
# Public signature added to every published comment (AI transparency).
SIGNATURE = (
    "Forecast by Aleph Zero, an AI agent running on Claude (Anthropic), "
    "operated under human supervision. Open-source code."
)
# Cheaper fallback ensemble (~$0.02/question) if credits run low:
# claude-haiku-5.5, gpt-5.6-luna, gemini-3.8-flash (prefix "openrouter/").
