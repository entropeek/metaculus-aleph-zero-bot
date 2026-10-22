"""AlephBot: template bot + multi-model ensemble, extra research, calibration and AI signature."""
import itertools

from forecasting_tools import GeneralLlm, MetaculusQuestion

from aleph_bot import config
from aleph_bot.calibration import CalibrationMixin
from aleph_bot.markets import market_context
from aleph_bot.prompts import BinaryPromptMixin
from aleph_bot.sources import source_context
from main import FallTemplateBot2026


def _llm(model: str) -> GeneralLlm:
    """Builds a forecasting model with reasoning effort and retries."""
    return GeneralLlm(
        model=model, temperature=0.3, timeout=240, allowed_tries=2,
        reasoning_effort=config.REASONING_EFFORT,
    )


# Prepended to every research text, so all question types (binary, numeric, MC) see it.
OPEN_QUESTION_GUARD = (
    "IMPORTANT: this question is still OPEN. Assume the resolving event has NOT happened yet "
    "unless a dated source below explicitly confirms it. Check units, thresholds and dates "
    "against the resolution criteria; check the date of every figure quoted.\n\n"
)


class AlephBot(CalibrationMixin, BinaryPromptMixin, FallTemplateBot2026):
    """Ensemble rotation, extra research, calibrated binary aggregation, AI signature."""

    _model_cycle = itertools.cycle(config.MODELS)

    def get_llm(self, purpose="default", guarantee_type=None):
        """Rotates the 'default' reasoning model; other purposes are unchanged."""
        llm = super().get_llm(purpose, guarantee_type)
        # Only the forecasting calls ask for ("default", "llm").
        if purpose == "default" and guarantee_type == "llm":
            llm = _llm(next(self._model_cycle))
        return llm

    async def run_research(self, question: MetaculusQuestion) -> str:
        """Template research (AskNews) + resolution source pages + market lookup."""
        criteria = f"{question.resolution_criteria or ''} {question.fine_print or ''}"
        research = OPEN_QUESTION_GUARD + await super().run_research(question)
        research += "\n\n" + await source_context(criteria)
        # Market lookup is optional and never blocks a forecast.
        if config.USE_MARKETS:
            research += "\n\n" + await market_context(question.question_text)
        return research

    def make_llm_dict(self) -> dict:
        """Lists the whole ensemble in the comment metadata, not only the first model."""
        return {**super().make_llm_dict(), "ensemble": config.MODELS}

    def _create_unified_explanation(self, *args, **kwargs) -> str:
        """Prepends the AI-transparency signature to the published comment."""
        return f"*{config.SIGNATURE}*\n\n" + super()._create_unified_explanation(*args, **kwargs)


def build_bot(publish: bool) -> AlephBot:
    """Creates the bot: SAMPLES_PER_MODEL forecasts per ensemble model, cheap parser, free research."""
    return AlephBot(
        research_reports_per_question=1,
        predictions_per_research_report=len(config.MODELS) * config.SAMPLES_PER_MODEL,
        use_research_summary_to_forecast=False,
        publish_reports_to_metaculus=publish,
        folder_to_save_reports_to=None,
        skip_previously_forecasted_questions=True,
        extra_metadata_in_explanation=True,
        llms={
            "default": _llm(config.MODELS[0]),
            "summarizer": config.PARSER,
            "researcher": config.RESEARCHER,
            "parser": config.PARSER,
        },
    )
