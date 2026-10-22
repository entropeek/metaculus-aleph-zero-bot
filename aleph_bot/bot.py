"""AlephBot: template bot + multi-model median, free market anchor and AI signature."""
import itertools

from forecasting_tools import GeneralLlm, MetaculusQuestion

from aleph_bot import config
from aleph_bot.markets import market_context
from main import FallTemplateBot2026


def _llm(model: str) -> GeneralLlm:
    """Builds a forecasting model with reasoning effort and retries."""
    return GeneralLlm(
        model=model, temperature=0.3, timeout=240, allowed_tries=2,
        reasoning_effort=config.REASONING_EFFORT,
    )


class AlephBot(FallTemplateBot2026):
    """Each forecast uses the next model of the ensemble; the parent takes the median."""

    _model_cycle = itertools.cycle(config.MODELS)

    def get_llm(self, purpose="default", guarantee_type=None):
        """Rotates the 'default' reasoning model; other purposes are unchanged."""
        llm = super().get_llm(purpose, guarantee_type)
        # Only the forecasting calls ask for ("default", "llm").
        if purpose == "default" and guarantee_type == "llm":
            llm = _llm(next(self._model_cycle))
        return llm

    async def run_research(self, question: MetaculusQuestion) -> str:
        """Template research (AskNews) followed by the free market lookup."""
        research = await super().run_research(question)
        # Market lookup is optional and never blocks a forecast.
        if config.USE_MARKETS:
            research = f"{research}\n\n{await market_context(question.question_text)}"
        return research

    def make_llm_dict(self) -> dict:
        """Lists the whole ensemble in the comment metadata, not only the first model."""
        return {**super().make_llm_dict(), "ensemble": config.MODELS}

    def _create_unified_explanation(self, *args, **kwargs) -> str:
        """Prepends the AI-transparency signature to the published comment."""
        return f"*{config.SIGNATURE}*\n\n" + super()._create_unified_explanation(*args, **kwargs)


def build_bot(publish: bool) -> AlephBot:
    """Creates the bot: one forecast per ensemble model, cheap parser, free research."""
    return AlephBot(
        research_reports_per_question=1,
        predictions_per_research_report=len(config.MODELS),
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
