"""Aleph Zero entry point: forecasts the FutureEval tournament and MiniBench under a cost cap."""
import argparse
import asyncio
import logging
import time

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


def run_once(bot, mode: str) -> None:
    """Forecasts every target once; stops spending once the per-run cap is reached."""
    reports = []
    with MonetaryCostManager(config.MAX_COST_PER_RUN) as cost:
        # One tournament after the other, errors are kept in the reports.
        for target in targets(mode):
            reports += asyncio.run(bot.forecast_on_tournament(target, return_exceptions=True))
        logging.info("Run cost: $%.4f", cost.current_usage)
    bot.log_report_summary(reports)


def main() -> None:
    """Runs once, or polls for --loop-hours (questions stay open only ~3 h)."""
    parser = argparse.ArgumentParser(description="Aleph Zero forecasting bot")
    parser.add_argument("--mode", choices=["tournament", "test"], default="tournament")
    parser.add_argument("--dry-run", action="store_true", help="forecast without publishing")
    parser.add_argument("--loop-hours", type=float, default=0, help="keep polling this long")
    parser.add_argument("--interval-minutes", type=float, default=10)
    args = parser.parse_args()
    bot = build_bot(publish=not args.dry_run)
    # Test mode re-forecasts questions already answered.
    bot.skip_previously_forecasted_questions = args.mode != "test"
    deadline = time.time() + args.loop_hours * 3600
    # Polling loop (one pass if --loop-hours is 0); a failed pass never ends the job.
    while True:
        try:
            run_once(bot, args.mode)
        except Exception:
            logging.exception("Pass failed, retrying at next interval")
        if time.time() + args.interval_minutes * 60 >= deadline:
            break
        time.sleep(args.interval_minutes * 60)


if __name__ == "__main__":
    main()
