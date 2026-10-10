"""Lesson 03 — Zero-shot vs few-shot, MEASURED on a labelled dataset.

Run:  python -m week2.lesson_03_zero_vs_few_shot

Opinions about prompts are cheap. Accuracy on labelled data is not.
Task: route support tickets to one of 4 queues. Some tickets are deliberately
ambiguous — that's where examples (few-shot) usually earn their tokens.
"""
from collections import Counter

from ai_core import Assistant

LABELS = ["billing", "technical", "account", "sales"]

# Our house rules (that a model can't know without being told or shown):
#  - "can't log in" / password / 2FA -> account (not technical)
#  - refunds, invoices, charges        -> billing
#  - upgrade / pricing questions       -> sales (even if they mention the bill)
TEST_SET = [
    ("I was charged twice this month, please refund one.", "billing"),
    ("The export button throws error 500 every time.", "technical"),
    ("I can't log in, it says my password is wrong.", "account"),
    ("How much would it cost to add 20 more seats?", "sales"),
    ("My 2FA codes stopped working after I changed phones.", "account"),
    ("Can I get an invoice with our VAT number on it?", "billing"),
    ("If we move to the annual plan, will our bill go down?", "sales"),
    ("The app is really slow when loading large dashboards.", "technical"),
    ("Please change the email address on my profile.", "account"),
    ("Do you offer discounts for nonprofits?", "sales"),
    ("The API returns 401 even though my token is valid.", "technical"),
    ("Why did my card get declined at renewal?", "billing"),
]

FEW_SHOT_EXAMPLES = [
    ("Reset link never arrives when I click 'forgot password'.", "account"),
    ("We'd like to upgrade to Enterprise — what's the price?", "sales"),
    ("Your app crashes when I upload a PDF.", "technical"),
    ("I need a refund for last month's charge.", "billing"),
]

INSTRUCTIONS = (
    "You route customer support tickets. Reply with exactly one word from this list "
    f"and nothing else: {', '.join(LABELS)}."
)


def zero_shot(ticket: str) -> str:
    return ticket


def few_shot(ticket: str) -> list[dict]:
    # Examples as real user/assistant turns: the model sees "this is how I answered
    # before" — usually more reliable than examples pasted into one big string.
    msgs = []
    for text, label in FEW_SHOT_EXAMPLES:
        msgs += [{"role": "user", "content": text}, {"role": "assistant", "content": label}]
    return msgs + [{"role": "user", "content": ticket}]


def evaluate(name: str, build_input) -> None:
    bot = Assistant(instructions=INSTRUCTIONS)
    correct, errors, invalid = 0, [], Counter()
    for ticket, gold in TEST_SET:
        pred = bot.complete(build_input(ticket)).text.strip().lower().rstrip(".")
        if pred not in LABELS:
            invalid[pred] += 1
        if pred == gold:
            correct += 1
        else:
            errors.append((ticket, gold, pred))
    print(f"\n=== {name}: {correct}/{len(TEST_SET)} correct "
          f"({correct / len(TEST_SET):.0%}) | {bot.usage}")
    for ticket, gold, pred in errors:
        print(f"   ✗ expected {gold:<9} got {pred:<9} | {ticket}")
    if invalid:
        print(f"   invalid labels: {dict(invalid)}")


evaluate("ZERO-SHOT", zero_shot)
evaluate("FEW-SHOT (4 examples)", few_shot)

print("""
Discuss:
- Few-shot costs more input tokens on EVERY call. Was the accuracy gain worth it?
- Which errors were about house rules the model couldn't know? Examples teach
  conventions; instructions state them. Try adding the rules as text instead (exercise).
- 12 items is tiny: one flip = 8 percentage points. Week 6 builds a 50+ item eval.
""")
