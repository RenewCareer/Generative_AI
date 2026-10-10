"""Lesson 04 — Compare two prompts with a controlled experiment.

Run:  python -m week3.lesson_04_controlled_experiment            (repeats=2)
      python -m week3.lesson_04_controlled_experiment 3          (repeats=3)

"Prompt B feels better" is not evidence. A controlled experiment:
  - changes ONE thing (the prompt), holds everything else fixed
    (model, settings, inputs, metrics);
  - uses the SAME inputs for both variants;
  - repeats each input, because outputs vary run to run;
  - decides metrics BEFORE looking at outputs (no moving goalposts).
"""
import statistics
import sys

from ai_core import Assistant

from .readability import analyze

REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
CONCEPTS = ["a variable", "the internet", "machine learning", "a database", "encryption",
            "an algorithm"]

VARIANTS = {
    "A_simple": "Explain the concept to a beginner.",
    "B_structured": (
        "Explain the concept to an adult with zero technical background.\n"
        "- First sentence: a plain definition.\n"
        "- Then an everyday analogy starting with 'Think of it like'.\n"
        "- Then one concrete example.\n"
        "- Max 100 words. Sentences under 15 words. No headings or lists."
    ),
}

# Metrics fixed up-front. pass = all hard requirements met.
def score(text: str) -> dict:
    r = analyze(text)
    return {
        "words": r.words,
        "flesch": r.flesch,
        "has_analogy": "think of it like" in text.lower(),
        "pass": r.words <= 110 and r.flesch >= 60 and "think of it like" in text.lower(),
    }


results: dict[str, list[dict]] = {}
for name, instructions in VARIANTS.items():
    bot = Assistant(instructions=instructions, remember_history=False)  # fresh tracker per arm
    rows = []
    for concept in CONCEPTS:
        for _ in range(REPEATS):
            reply = bot.complete(f"Explain: {concept}")
            rows.append({**score(reply.text), "tokens": reply.total_tokens,
                         "latency": reply.latency_s, "cost": reply.cost_usd or 0})
    results[name] = rows
    print(f"done {name}: {len(rows)} samples")


def summarise(rows: list[dict], key: str) -> str:
    vals = [float(r[key]) for r in rows]
    sd = statistics.stdev(vals) if len(vals) > 1 else 0
    return f"{statistics.mean(vals):8.1f} ±{sd:5.1f}"


print(f"\n{'metric':<14}" + "".join(f"{n:>22}" for n in results))
for key in ("words", "flesch", "tokens", "latency"):
    print(f"{key:<14}" + "".join(f"{summarise(rows, key):>22}" for rows in results.values()))
for key in ("has_analogy", "pass"):
    print(f"{key + ' rate':<14}" + "".join(
        f"{sum(r[key] for r in rows) / len(rows):>22.0%}" for rows in results.values()))
print(f"{'total cost $':<14}" + "".join(
    f"{sum(r['cost'] for r in rows):>22.5f}" for rows in results.values()))

print("""
How to read this
- Compare means AND spread (±). A variant with a better mean but huge spread is
  less predictable — and predictability is what products need.
- With 6 concepts x 2 repeats, small differences are noise. More samples = more trust.
- "pass rate" is the number you'd put in a decision doc. The others explain WHY.
- Next: Week 6 adds labelled data, statistical comparisons and regression tests.
""")
