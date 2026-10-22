"""Aleph Zero bot settings, all overridable through environment variables."""
import os

# Forecasting models, one forecast each; the median is published (comma-separated litellm names).
MODELS = os.getenv(
    "ALEPH_MODELS",
    "openrouter/deepseek/deepseek-chat,openrouter/google/gemini-2.5-flash,openrouter/openai/gpt-4o-mini",
).split(",")
# Cheap model that extracts the number from each model's reasoning.
PARSER = os.getenv("ALEPH_PARSER", "openrouter/openai/gpt-4o-mini")
# Free for participants: AskNews news summaries.
RESEARCHER = os.getenv("ALEPH_RESEARCHER", "asknews/news-summaries")
# Hard spending cap per run, in USD (one run every 20 minutes).
MAX_COST_PER_RUN = float(os.getenv("ALEPH_MAX_COST_PER_RUN", "2.0"))
# Free prediction-market lookup (Manifold, Polymarket) added to the research.
USE_MARKETS = os.getenv("ALEPH_USE_MARKETS", "true").lower() == "true"
# Public signature added to every published comment (AI transparency).
SIGNATURE = (
    "Forecast by Aleph Zero, an AI agent running on Claude (Anthropic), "
    "operated under human supervision. Open-source code."
)
