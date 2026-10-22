"""Research mixin: open-question guard, AskNews, resolution-source pages, markets and anchor."""
from forecasting_tools import BinaryQuestion, MetaculusQuestion

from aleph_bot import config
from aleph_bot.anchor import judge
from aleph_bot.markets import market_search, render
from aleph_bot.sources import source_context

# Prepended to every research text, so all question types (binary, numeric, MC) see it.
OPEN_QUESTION_GUARD = (
    "IMPORTANT: this question is still OPEN. Assume the resolving event has NOT happened yet "
    "unless a dated source below explicitly confirms it. Check units, thresholds and dates "
    "against the resolution criteria; check the date of every figure quoted.\n\n"
)


class ResearchMixin:
    """Extends the template research and records a verified market anchor per binary question."""

    # Anchor probability per question URL, read later by CalibrationMixin.
    anchors: dict[str, float] = {}

    async def run_research(self, question: MetaculusQuestion) -> str:
        """Template research (AskNews) + resolution source pages + market lookup and judge."""
        criteria = f"{question.resolution_criteria or ''} {question.fine_print or ''}"
        research = OPEN_QUESTION_GUARD + await super().run_research(question)
        research += "\n\n" + await source_context(criteria)
        # Market lookup is optional and never blocks a forecast.
        if config.USE_MARKETS:
            markets = await market_search(question.question_text)
            research += "\n\n" + render(markets)
            liquid = [m for m in markets if m["liquid"]]
            # Anchors are only used for plain binary questions.
            if isinstance(question, BinaryQuestion):
                anchor = await judge(self.get_llm("parser", "llm"), question, liquid)
                self.anchors[question.page_url] = anchor
        return research
