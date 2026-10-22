# Aleph Zero forecasting bot

Built by **Aleph Zero**, an AI agent running on Claude (Anthropic), under the supervision of its human operator.
Fork of [metac-bot-template](https://github.com/Metaculus/metac-bot-template). Every published comment carries this disclosure.

## Approach (low cost)
- Research: AskNews news summaries (free for participants) + resolution-source pages + free prediction-market quotes (Manifold, Polymarket) as a weak anchor. Numeric questions linking a FRED series also get a random-walk baseline from that series' public history (backtest: 90% intervals cover 90% of outcomes).
- Forecast: 3 forecasts per question (1 per model; `ALEPH_SAMPLES=2` doubles it), rotated across an ensemble (Claude Sonnet 5.5, GPT-6.1 Sol, Gemini 4 Argon by default; credits cover only OpenAI, Anthropic, Google). Binary: mean of log-odds × 1.1, blended 50/50 in log-odds with a prediction market only when a cheap LLM judge confirms it is the same event/threshold/deadline and it is liquid, capped to [2%, 98%]; other types (incl. conditional questions): framework median. Every research text starts with an "open question" guard. Rotation is shared across concurrent questions, so a question may occasionally get the same model twice.
- Estimated cost: ~$0.12/question (OpenRouter prices of 2026-10-22, not yet measured), plus one cheap judge call when liquid markets are found, cheaper fallback in `aleph_bot/config.py`.
- Cost: hard cap per run (`ALEPH_MAX_COST_PER_RUN`, default $3).

## Setup (human operator)
1. Secrets: `METACULUS_TOKEN`, `OPENROUTER_API_KEY` (Metaculus credits), `ASKNEWS_CLIENT_ID`, `ASKNEWS_SECRET`.
2. Optional variables: `ALEPH_MODELS`, `ALEPH_PARSER` (check model names and prices on OpenRouter first).
3. Run the "Test Bot" workflow or `python aleph_main.py --mode test --dry-run`.
4. Scheduled workflows only run on the default branch (`main`).
5. GitHub may pause scheduled workflows in a public repo after 60 days without commits: push a small commit before ~2026-12-20.
