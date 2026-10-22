# Aleph Zero forecasting bot

Built by **Aleph Zero**, an AI agent running on Claude (Anthropic), under the supervision of its human operator.
Fork of [metac-bot-template](https://github.com/Metaculus/metac-bot-template). Every published comment carries this disclosure.

## Approach (low cost, ~$0.15 max per question)
- Research: AskNews news summaries (free for participants) + free prediction-market quotes (Manifold, Polymarket) as a weak anchor.
- Forecast: one forecast per ensemble model (3 cheap models by default), median published.
- Cost: hard cap per run (`ALEPH_MAX_COST_PER_RUN`, default $2).

## Setup (human operator)
1. Secrets: `METACULUS_TOKEN`, `OPENROUTER_API_KEY` (Metaculus credits), `ASKNEWS_CLIENT_ID`, `ASKNEWS_SECRET`.
2. Optional variables: `ALEPH_MODELS`, `ALEPH_PARSER` (check model names and prices on OpenRouter first).
3. Run the "Test Bot" workflow or `python aleph_main.py --mode test --dry-run`.
