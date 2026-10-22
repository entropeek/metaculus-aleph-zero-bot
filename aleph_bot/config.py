"""Aleph Zero bot settings, all overridable through environment variables."""
import os

# Forecasting models, one forecast each; the median is published (comma-separated litellm names).
MODELS = os.getenv(
    "ALEPH_MODELS",
    # ~$0.09/question at 2026-10-22 OpenRouter prices; Google avoided (shared 150 rpm limit).
    "openrouter/anthropic/claude-sonnet-5.5,openrouter/openai/gpt-6.1-sol,openrouter/deepseek/deepseek-v4-pro",
).split(",")
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
