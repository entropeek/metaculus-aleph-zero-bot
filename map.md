# Code map (Aleph Zero additions; upstream template files unchanged)
- aleph_main.py : entry point; tournament + MiniBench (or `--mode test`), per-run cost cap, `--dry-run`.
- aleph_bot/config.py : models, parser, researcher, cost cap, markets flag, AI signature (env-overridable).
- aleph_bot/bot.py : AlephBot = template bot + model rotation (median of ensemble), market anchor, signature.
- aleph_bot/markets.py : free Manifold / Polymarket search, failure-tolerant.
- .github/workflows/run_bot_on_tournament.yaml : now runs aleph_main.py.
- .github/workflows/run_bot_on_metaculus_cup.yaml : schedule disabled (credits saved).
- Upstream: main.py (template bot, base class), bot_helpers.py, main_with_no_framework.py.
