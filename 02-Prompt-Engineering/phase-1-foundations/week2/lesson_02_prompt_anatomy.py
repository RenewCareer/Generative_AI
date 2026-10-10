"""Lesson 02 — Anatomy of a prompt: Role, Task, Context, Constraints, Output format.

Run:  python -m week2.lesson_02_prompt_anatomy

We send the SAME request twice: once as most people write it, once with every
component made explicit. Compare the outputs and ask: which one could I put in
a product and get the same shape of answer every time?
"""
from ai_core import Assistant


def build_prompt(*, role: str, task: str, context: str, constraints: list[str],
                 output_format: str) -> tuple[str, str]:
    """Returns (instructions, input). Role + constraints + format are stable rules
    -> instructions. Task + context change per request -> input."""
    instructions = "\n".join([
        f"# Role\n{role}",
        "# Constraints\n" + "\n".join(f"- {c}" for c in constraints),
        f"# Output format\n{output_format}",
    ])
    user_input = f"# Task\n{task}\n\n# Context\n<context>\n{context}\n</context>"
    return instructions, user_input


bot = Assistant(instructions=None)

vague = "write something about our new feature for customers"

instructions, structured = build_prompt(
    role="You are a product marketing writer for a B2B SaaS company. Your readers are "
         "busy operations managers, not engineers.",
    task="Write the in-app announcement for the feature described in the context.",
    context="Feature: Scheduled Reports. Users can now schedule any dashboard to be "
            "emailed as a PDF daily, weekly or monthly. Available on Pro and Enterprise "
            "plans. Set up from the 'Share' menu on any dashboard. Launch date: 3 Nov.",
    constraints=[
        "Maximum 80 words.",
        "Lead with the benefit to the reader, not the feature name.",
        "Mention which plans include it.",
        "No exclamation marks, no buzzwords like 'revolutionary' or 'game-changing'.",
        "Only use facts from the context. Do not invent features.",
    ],
    output_format="A headline (max 8 words) on the first line, a blank line, then the "
                  "body as one paragraph, then a blank line and a call-to-action line "
                  "starting with 'Try it:'.",
)

for title, (instr, inp) in {"VAGUE": (None, vague), "STRUCTURED": (instructions, structured)}.items():
    r = bot.complete(inp, instructions=instr)
    print(f"\n==================== {title} ====================\n{r.text}\n\n{r.stats()}")

print("""
Checklist for every prompt you write:
  Role        - who is answering, for whom?        (sets vocabulary, tone, expertise)
  Task        - one clear verb: write / classify / extract / explain / critique
  Context     - the facts the model needs and can't guess, clearly delimited
  Constraints - length, tone, must / must-not, what to do when info is missing
  Format      - exact shape of the output, so code (or a person) can rely on it
""")
