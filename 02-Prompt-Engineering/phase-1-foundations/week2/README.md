# Week 2 — Prompt design and instruction hierarchy

**Goal:** write prompts that behave the same way every time, and *prove* it with tests.

**Practical:** a prompt library of 20 tested templates → [`prompt_library/`](prompt_library/)

---

## Day 1 — Instruction hierarchy

```bash
python -m week2.lesson_01_instruction_hierarchy
```

```
 developer / system   ← instructions=..., role "developer"   (your product's rules)
        ▲ wins on conflict
 user                 ← role "user"                          (the person's request)
        ▲
 data inside messages ← documents, emails, web pages, tool output (NOT instructions at all)
```

- Rules that never change → `instructions`. The request that changes every call → `input`.
- Say what's **flexible** too ("follow the user's formatting preferences unless they conflict with the rules above"), or the bot becomes rigid.
- The hierarchy is a strong *trained tendency*, not a security guarantee. Week 12 (prompt injection) builds on this.

## Day 2 — Anatomy of a prompt

```bash
python -m week2.lesson_02_prompt_anatomy
```

| Part | Question it answers | Weak | Strong |
|---|---|---|---|
| **Role** | Who's answering, for whom? | "You are an AI" | "Product writer for busy ops managers, not engineers" |
| **Task** | What exactly to do? | "write something" | "Write the in-app announcement" |
| **Context** | What facts are needed? | (none — model invents) | Feature, plans, date, in `<context>` |
| **Constraints** | Limits & must/must-nots | "make it good" | "≤80 words, lead with benefit, only facts from context" |
| **Output format** | What shape? | (anything) | "Headline / blank / paragraph / 'Try it:' line" |

The test: *could a new colleague do this task well from your prompt alone?* If not, neither can the model.

## Day 3 — Zero-shot vs few-shot

```bash
python -m week2.lesson_03_zero_vs_few_shot
```

- **Zero-shot**: instructions only. Cheap. Great when the task is common and the rules are obvious.
- **Few-shot**: add examples. Use when there are **conventions the model can't guess** (your labels, your edge cases, your format).
- Good examples: cover the hard/edge cases, are diverse, are *correct*, and match the real input format. The model copies everything — including your mistakes and accidental patterns (e.g. if 3 of 4 examples are "billing", it'll lean billing).
- Few-shot isn't free: those tokens are paid on **every** call.
- **Decide with data**, not vibes. That's why the lesson prints accuracy.

## Day 4 — Delimiters, negatives, ambiguity, conflicts

```bash
python -m week2.lesson_04_delimiters_ambiguity_conflicts
```

1. **Delimiters** separate instructions from data: `<document>…</document>`. Name the tag in the instructions.
2. **Negative instructions** ("don't be technical") name the thing and leave the target open. Prefer positive targets ("words a 12-year-old knows"); keep "never…" for hard limits.
3. **Ambiguity** is a spec bug. Either fill the gap or explicitly allow the model to ask.
4. **Conflicts** happen in real specs. Give a **priority order** and ask the model to state its trade-off.

## Day 5 — Templates, versioning, the library

```bash
python -m week2.prompt_library.run_tests --validate-only       # free, static checks
python -m week2.prompt_library.run_tests -t classify_ticket -v  # one template, verbose
python -m week2.prompt_library.run_tests                        # all 20 (~35 calls, a few cents on a mini model)
python -m week2.prompt_library.run_tests --repeat 3             # flakiness check
```

Anatomy of a template file ([example](prompt_library/templates/04_classify_ticket.toml)):

```toml
name = "classify_ticket"
version = "1.0.0"                  # bump on every change (semver)
variables = ["ticket"]
changelog = ["1.0.0 initial"]
instructions = """..."""           # stable rules
template = """<ticket>${ticket}</ticket>"""   # ${var} — JSON braces stay safe

[[tests]]                           # tests live WITH the prompt
name = "annual_plan_is_sales"
[tests.vars]
ticket = "If we switch to annual, will our bill go down?"
[[tests.checks]]
type = "equals"
value = "sales"
```

**Versioning rules**
- PATCH (1.0.**1**): wording tweak, same behaviour expected.
- MINOR (1.**1**.0): new capability, old outputs still valid.
- MAJOR (**2**.0.0): output format changes — anything parsing it must change too.
- Never edit a prompt without re-running its tests. Results are saved in `results/` with `template@version` + model so you can compare before/after.

Available check types live in [`checks.py`](prompt_library/checks.py): `equals`, `one_of`, `contains_all/any/none`, `regex`, `max_words`, `min_words`, `line_count`, `max_lines`, `json_valid`, `json_keys`, `json_array_len`, `ends_with_question`.

---

## ✅ Exercises

1. **Run the full library.** Which templates fail? For each failure decide: is the *prompt* wrong, the *test* too strict, or the *model* not capable? Fix and bump versions.
2. **Rules vs examples.** In lesson 03, replace the few-shot examples with the house rules written as text. Then try both together. Record accuracy + input tokens for all three variants.
3. **Flakiness.** Run `--repeat 5`. Any template below 100%? A prompt that passes 4/5 times fails 20% of your users.
4. **Model swap.** Run the library on a smaller model (`--model gpt-5-nano` or similar). Which templates degrade? That's your list of "needs a bigger model" tasks.
5. **Add 3 templates of your own** from your real work, each with ≥2 tests including one edge case. Keep `pytest` green.

**Self-check:**
- Where should a "never discuss competitors" rule go, and why not in the user message?
- When is few-shot worth its token cost?
- Why `${var}` instead of `{var}` for templates?
- What's the difference between a static test and a live test of a prompt?
