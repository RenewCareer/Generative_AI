"""The lesson-generation workflow.

    plan (JSON) ──verify_plan──> write (Markdown) ──┐
                                                    ▼
             ┌──── revise <── issues? ── verify (code) + critique (LLM)
             │                                │ no issues
             └────────────────────────────────┴──> done

Each step is a separate, small, testable function with its own prompt.
`bot` is injected, so tests run the whole pipeline with a fake client.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable

from ai_core import Assistant, AssistantError

from ..readability import analyze
from .prompts import CRITIC, PLANNER, PROMPT_VERSION, REVISER, WRITER
from .verify import verify_lesson, verify_plan

MIN_SCORE = 4


@dataclass
class Round:
    number: int
    words: int
    flesch: float
    verify_issues: list[str]
    scores: dict
    critic_issues: list[str]

    @property
    def passed(self) -> bool:
        return not self.verify_issues and not self.critic_issues


@dataclass
class LessonResult:
    topic: str
    audience: str
    model: str
    prompt_version: str
    plan: dict
    markdown: str
    rounds: list[Round] = field(default_factory=list)
    usage: str = ""

    @property
    def passed(self) -> bool:
        return bool(self.rounds) and self.rounds[-1].passed

    def report(self) -> dict:
        d = asdict(self)
        d.pop("markdown")
        d["passed"] = self.passed
        return d


def make_plan(bot: Assistant, topic: str, audience: str) -> dict:
    plan, _ = bot.complete_json(f"Topic: {topic}", instructions=PLANNER.format(audience=audience))
    problems = verify_plan(plan)
    if problems:  # one corrective retry, telling the model exactly what was wrong
        plan, _ = bot.complete_json(
            f"Topic: {topic}\nYour previous plan had problems: {problems}\nPrevious plan: {plan}",
            instructions=PLANNER.format(audience=audience))
        problems = verify_plan(plan)
        if problems:
            raise AssistantError(f"Planner produced an invalid plan: {problems}",
                                 "Inspect the PLANNER prompt or try a stronger model.")
    return plan


def write_lesson(bot: Assistant, topic: str, audience: str, plan: dict) -> str:
    return bot.complete(f"Topic: {topic}\n<plan>\n{plan}\n</plan>",
                        instructions=WRITER.format(audience=audience)).text


def critique(bot: Assistant, md: str, audience: str) -> tuple[dict, list[str]]:
    data, _ = bot.complete_json(f"<lesson>\n{md}\n</lesson>",
                                instructions=CRITIC.format(audience=audience))
    scores = {k: int(v) for k, v in data.get("scores", {}).items()}
    issues = [str(i) for i in data.get("issues", [])]
    # Only act on critic issues when a score is actually low: stops endless nitpicking.
    if scores and min(scores.values()) >= MIN_SCORE:
        issues = []
    elif not scores:
        issues = issues or ["Critic returned no scores."]
    return scores, issues


def revise(bot: Assistant, md: str, audience: str, problems: list[str]) -> str:
    listed = "\n".join(f"- {p}" for p in problems)
    return bot.complete(f"<lesson>\n{md}\n</lesson>\n<problems>\n{listed}\n</problems>",
                        instructions=REVISER.format(audience=audience)).text


def generate_lesson(topic: str, audience: str = "complete beginners", *,
                    bot: Assistant | None = None, max_revisions: int = 2,
                    log: Callable[[str], None] = print) -> LessonResult:
    bot = bot or Assistant(remember_history=False)

    log(f"[plan]  {topic}")
    plan = make_plan(bot, topic, audience)
    log(f"[write] '{plan['title']}'")
    md = write_lesson(bot, topic, audience, plan)

    result = LessonResult(topic, audience, bot.model, PROMPT_VERSION, plan, md)
    for n in range(max_revisions + 1):
        # Verify with code first; only pay for the critic if the lesson is structurally OK.
        v_issues = verify_lesson(md, plan)
        scores, c_issues = ({}, []) if v_issues else critique(bot, md, audience)
        r = analyze(md)
        rnd = Round(n, r.words, r.flesch, v_issues, scores, c_issues)
        result.rounds.append(rnd)
        log(f"[check] round {n}: {r.words} words, Flesch {r.flesch}, scores {scores or '-'}, "
            f"{len(v_issues)} verify + {len(c_issues)} critic issues")
        if rnd.passed or n == max_revisions:
            break
        log("[revise]")
        md = revise(bot, md, audience, v_issues + c_issues)

    result.markdown = md
    result.usage = str(bot.usage)
    log(f"[done]  {'PASS' if result.passed else 'NEEDS HUMAN REVIEW'} | {bot.usage}")
    return result
