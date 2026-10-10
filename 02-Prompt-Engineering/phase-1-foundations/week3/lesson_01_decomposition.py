"""Lesson 01 — Task decomposition: one mega-prompt vs a multi-step workflow.

Run:  python -m week3.lesson_01_decomposition

Task: analyse 10 customer reviews and report how many mention each issue.
We KNOW the true counts, so we can check who's right.

  A. Mega-prompt: "read all of these, count issues, write a summary"
  B. Workflow:  (1) LLM labels each review  -> JSON, one small focused call each
                (2) Python counts             -> exact, free, deterministic
                (3) LLM writes the summary    -> from verified numbers

The senior lesson: give the LLM the fuzzy parts (reading language) and give
code the exact parts (counting, maths, sorting). LLMs are bad calculators.
"""
from collections import Counter

from ai_core import Assistant

ISSUES = ["delivery", "price", "quality", "support", "app"]

REVIEWS = [
    ("Arrived 9 days late and the box was crushed.", {"delivery"}),
    ("Great quality but honestly too expensive for what it is.", {"quality", "price"}),
    ("Support never answered my emails. Twice.", {"support"}),
    ("The app keeps logging me out, very annoying.", {"app"}),
    ("Stitching came apart after one wash.", {"quality"}),
    ("Fast shipping, fair price, happy overall!", set()),
    ("Courier left it in the rain, and the helpline was useless.", {"delivery", "support"}),
    ("Cheaper elsewhere. Also the app crashes at checkout.", {"price", "app"}),
    ("Late delivery again. Third time this year.", {"delivery"}),
    ("Fabric feels cheap and thin.", {"quality"}),
]
TRUE_COUNTS = Counter(i for _, labels in REVIEWS for i in labels)

bot = Assistant(instructions=None)
numbered = "\n".join(f"{n}. {text}" for n, (text, _) in enumerate(REVIEWS, 1))

# ---- A. Mega-prompt -------------------------------------------------------
print("=== A. One mega-prompt ===")
data_a, _ = bot.complete_json(
    f"<reviews>\n{numbered}\n</reviews>\n\nCount how many reviews mention each issue "
    f"({', '.join(ISSUES)}) as complaints, then write a 2-sentence executive summary. "
    'Return JSON: {"counts": {issue: int}, "summary": str}'
)
counts_a = {k: int(v) for k, v in data_a["counts"].items()}

# ---- B. Workflow ------------------------------------------------------------
print("=== B. Decomposed workflow ===")
labeler = ("Label which issues a customer review COMPLAINS about. Allowed issues: "
           f"{', '.join(ISSUES)}. Praise is not a complaint. "
           'Return JSON: {"issues": [..]} (empty list if none).')
counts_b: Counter = Counter()
for text, _ in REVIEWS:  # step 1: one small, focused, checkable call per item
    labels, _ = bot.complete_json(f"<review>{text}</review>", instructions=labeler)
    counts_b.update(i for i in labels["issues"] if i in ISSUES)  # validate against taxonomy

summary_b = bot.complete(  # step 3: write from verified facts only
    f"Issue counts from {len(REVIEWS)} reviews: {dict(counts_b.most_common())}. "
    "Write a 2-sentence executive summary naming the top problem and a suggested action. "
    "Use only these numbers.").text

# ---- Compare ----------------------------------------------------------------
print(f"\n{'issue':<10}{'truth':>7}{'A mega':>8}{'B flow':>8}")
for issue in ISSUES:
    t, a, b = TRUE_COUNTS[issue], counts_a.get(issue, 0), counts_b[issue]
    print(f"{issue:<10}{t:>7}{a:>7}{'' if a == t else '✗':1}{b:>7}{'' if b == t else '✗':1}")
print(f"\nA summary: {data_a['summary']}\nB summary: {summary_b}")
print(f"\nTotal usage: {bot.usage}")

print("""
Discuss:
- Which approach got the counts right? Which was cheaper? Which is easier to debug
  when it's wrong? (In B you can inspect the label of every single review.)
- B makes 12 calls. In production you'd run step 1 in parallel (Week 13: async).
- Decomposition costs latency and tokens; buy it when accuracy or debuggability matters.
""")
