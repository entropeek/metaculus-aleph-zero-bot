"""Market anchor: a cheap LLM judge accepts a market only if it is the same event, threshold and deadline."""
import re

from forecasting_tools import clean_indents

JUDGE_PROMPT = """
    You check whether a prediction market resolves on EXACTLY the same outcome as a forecasting question.

    Question: {question}
    Resolution criteria: {criteria}
    Question closes/resolves around: {deadline}

    Markets:
    {markets}

    A market matches only if it has the same event, the same threshold/number and a deadline within
    a few days of the question's. Similar topic is NOT enough. If in doubt, answer NONE.
    The last line of your answer must be exactly "MATCH: <market number>" or "NONE".
    """


def judge_prompt(question, markets: list[dict]) -> str:
    """Builds the judge prompt listing numbered candidate markets."""
    listing = "\n".join(f"{i}. [{m['source']}] {m['question']} (ends {m['end']})" for i, m in enumerate(markets, 1))
    return clean_indents(JUDGE_PROMPT.format(
        question=question.question_text, criteria=question.resolution_criteria,
        deadline=question.scheduled_resolution_time, markets=listing))


def parse_verdict(answer: str, markets: list[dict]) -> float | None:
    """Price of the chosen market (taken from the data, never from the LLM text), or None."""
    found = re.findall(r"MATCH:\s*(\d+)", answer or "")
    index = int(found[-1]) - 1 if found else -1
    # Out-of-range or missing choice means no anchor.
    return markets[index]["prob"] if 0 <= index < len(markets) else None


async def judge(llm, question, markets: list[dict]) -> float | None:
    """Asks the judge model; no candidates or any error gives no anchor."""
    verdict = None
    # Only liquid markets can become anchors; skip the LLM call when there are none.
    if markets:
        try:
            verdict = parse_verdict(await llm.invoke(judge_prompt(question, markets)), markets)
        except Exception:  # Judge failure must never block the forecast.
            verdict = None
    return verdict
