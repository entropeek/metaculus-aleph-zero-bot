"""Binary prompt with superforecasting habits: outside view first, base rates, unresolved guard."""
from datetime import datetime

from forecasting_tools import BinaryQuestion, clean_indents


def binary_prompt(question: BinaryQuestion, research: str, disclaimer: str) -> str:
    """Builds the binary forecasting prompt (outside view, then inside view)."""
    return clean_indents(
        f"""
        You are a superforecaster with an excellent calibration record.

        Question: {question.question_text}
        Background: {question.background_info}
        Resolution criteria (NOT yet satisfied; the question is still open): {question.resolution_criteria}
        {question.fine_print}

        Research (news, resolution-source pages, related markets; may contain errors):
        {research}

        Today is {datetime.now().strftime("%Y-%m-%d")}.

        Work through these steps briefly:
        (a) Time left until resolution, and the status quo outcome if nothing changes.
        (b) Outside view: a reference class and its base rate (how often such events happen in such a window).
        (c) Inside view: specific evidence that moves you away from the base rate, and by how much.
        (d) A scenario for Yes and a scenario for No.
        (e) Check the exact wording of the criteria: what precisely must happen, by when, per which source.
        (f) Related market prices, if they truly match this question, are a strong signal; otherwise ignore them.
        Be decisive: avoid 50% unless the evidence is truly balanced; avoid extremes unless nearly certain.
        {disclaimer}

        The last thing you write is your final answer as: "Probability: ZZ%", 0-100
        """
    )


class BinaryPromptMixin:
    """Uses binary_prompt instead of the template prompt."""

    async def _run_forecast_on_binary(self, question, research):
        """Same pipeline as the template, with the Aleph Zero prompt."""
        disclaimer = self._get_conditional_disclaimer_if_necessary(question)
        return await self._binary_prompt_to_forecast(question, binary_prompt(question, research, disclaimer))
