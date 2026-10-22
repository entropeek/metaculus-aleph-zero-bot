"""Aleph Zero entry point: forecasts the FutureEval tournament and MiniBench under a cost cap."""
import argparse
import asyncio
import logging

from forecasting_tools import MetaculusClient, MonetaryCostManager

from aleph_bot import config
from aleph_bot.bot import build_bot

logging.basicConfig(level=logging.INFO)


def targets(mode: str) -> list:
    """Tournament ids to forecast for the chosen mode."""
    client = MetaculusClient()
    # 'test' = bot-testing-area, the recommended smoke test target.
    return (
        ["bot-testing-area"]
        if mode == "test"
        else [client.CURRENT_AI_COMPETITION_ID, client.CURRENT_MINIBENCH_ID]
    )


def main() -> None:
    """Runs every target; stops spending once the per-run cap is reached."""
    parser = argparse.ArgumentParser(description="Aleph Zero forecasting bot")
    parser.add_argument("--mode", choices=["tournament", "test"], default="tournament")
    parser.add_argument("--dry-run", action="store_true", help="forecast without publishing")
    args = parser.parse_args()
    bot = build_bot(publish=not args.dry_run)
    # Test mode re-forecasts questions already answered.
    bot.skip_previously_forecasted_questions = args.mode != "test"
    reports = []
    with MonetaryCostManager(config.MAX_COST_PER_RUN) as cost:
        # One tournament after the other, errors are kept in the reports.
        for target in targets(args.mode):
            reports += asyncio.run(bot.forecast_on_tournament(target, return_exceptions=True))
        logging.info("Run cost: $%.4f", cost.current_usage)
    bot.log_report_summary(reports)


if __name__ == "__main__":
    main()
