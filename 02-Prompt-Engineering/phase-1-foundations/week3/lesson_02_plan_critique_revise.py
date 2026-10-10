"""Lesson 02 — Plan -> Draft -> Critique -> Revise -> Verify.

Run:  python -m week3.lesson_02_plan_critique_revise "recursion"

  plan      the model decides WHAT to say before HOW (structure first)
  draft     write from the plan
  critique  a separate call grades the draft against an explicit rubric (JSON)
  verify    code checks the measurable rules (length, readability)
  revise    fix exactly the listed problems; loop until pass or max rounds

Why a SEPARATE critique call? The writer is anchored on its own text. A fresh
call with a reviewer role and a rubric finds problems the writer won't.
Why code verification too? Models are poor judges of their own word counts.
"""
import sys

from ai_core import Assistant

from .readability import analyze

TOPIC = sys.argv[1] if len(sys.argv) > 1 else "recursion"
MAX_ROUNDS = 3
MAX_WORDS, MIN_FLESCH = 220, 60

bot = Assistant(instructions=None)

RUBRIC = """Score 1-5 each:
- accuracy: technically correct, no misleading simplification
- beginner_fit: no unexplained jargon, assumes zero prior knowledge
- concreteness: has a relatable analogy AND a concrete example
- structure: ideas build in a logical order"""

# 1. PLAN
plan, _ = bot.complete_json(
    f"Plan a short beginner explanation of '{TOPIC}'. Return JSON: "
    '{"key_points": [3 short strings, in teaching order], "analogy": str, '
    '"example": str, "misconception_to_address": str}',
    instructions="You are a curriculum designer for absolute beginners.")
print("PLAN:", plan)

# 2. DRAFT
draft = bot.complete(
    f"Topic: {TOPIC}\nPlan:\n{plan}",
    instructions=f"Write a beginner explanation following the plan exactly. Plain prose, "
                 f"short sentences, max {MAX_WORDS} words, no headings.").text

for round_ in range(1, MAX_ROUNDS + 1):
    # 3. VERIFY (code) + CRITIQUE (model)
    r = analyze(draft)
    hard_issues = []
    if r.words > MAX_WORDS:
        hard_issues.append(f"Too long: {r.words} words, limit {MAX_WORDS}.")
    if r.flesch < MIN_FLESCH:
        hard_issues.append(f"Too hard to read (Flesch {r.flesch} < {MIN_FLESCH}): "
                           f"use shorter sentences and simpler words.")

    critique, _ = bot.complete_json(
        f"<explanation>\n{draft}\n</explanation>",
        instructions=f"You are a strict reviewer of beginner learning material.\n{RUBRIC}\n"
                     'Return JSON: {"scores": {criterion: int}, "issues": [specific, '
                     'actionable problems; empty if none]}')
    scores = critique["scores"]
    soft_issues = critique["issues"] if min(scores.values()) < 4 else []

    print(f"\n--- round {round_}: {r.words} words, Flesch {r.flesch}, scores {scores}")
    for i in hard_issues + soft_issues:
        print(f"    • {i}")
    if not hard_issues and not soft_issues:
        print("    ✓ passes verification and rubric")
        break
    if round_ == MAX_ROUNDS:
        print("    ✗ still failing after max rounds — a human should look at this")
        break

    # 4. REVISE — targeted: give the exact problems, ask to keep what works
    draft = bot.complete(
        f"<explanation>\n{draft}\n</explanation>\n<problems>\n"
        + "\n".join(f"- {i}" for i in hard_issues + soft_issues) + "\n</problems>",
        instructions="Revise the explanation to fix every listed problem. Keep everything "
                     "that is not mentioned. Output only the revised explanation.").text

print(f"\n=== FINAL ===\n{draft}\n\n{bot.usage}")
print("""
Discuss:
- Did the critic find real problems or nitpick? A rubric with concrete criteria
  produces more useful critiques than "rate this 1-10".
- Always cap the loop. Without MAX_ROUNDS, a picky critic = infinite bill.
- LLM-as-judge has biases (prefers longer text, its own style). Week 6 calibrates it
  against human labels.
""")
