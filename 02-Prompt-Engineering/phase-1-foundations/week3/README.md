# Week 3 — Advanced prompting strategies

**Goal:** stop writing one big prompt and hoping. Build *workflows* of small prompts plus code, and *prove* which version is better.

**Practical:** an AI lesson generator that produces consistent beginner-level lessons → [`lesson_generator/`](lesson_generator/)

---

## Day 1 — Task decomposition

```bash
python -m week3.lesson_01_decomposition
```

| | Mega-prompt | Workflow |
|---|---|---|
| Calls | 1 | many small ones |
| Debuggable | ❌ one blob | ✅ inspect each step |
| Exact maths/counting | ❌ LLMs guess | ✅ Python does it |
| Latency/cost | lower | higher (parallelise later) |

**Rule:** LLM for language (read, label, write). Code for logic (count, sort, compare, validate). Validate every LLM output against what you expect (e.g. the allowed label list) before the next step uses it.

## Day 2 — Plan, critique, revise, verify

```bash
python -m week3.lesson_02_plan_critique_revise "recursion"
```

- **Plan first** — structure before prose makes outputs consistent across runs.
- **Critique in a separate call** with a **rubric** — specific criteria give actionable critiques; "rate 1-10" gives noise.
- **Verify with code** whatever is measurable (length, sections, readability, required terms). Cheap, exact, run it *first*.
- **Revise with the exact problem list**, and "keep everything else".
- **Always cap the loop** (`MAX_ROUNDS`). After the cap → flag for a human. That's not failure; that's a system knowing its limits.

## Day 3 — Prompt chaining & routing

```bash
python -m week3.lesson_03_routing
```

- **Chaining** = output of step N is input of step N+1 (Day 1 & 2 are chains).
- **Routing** = a classifier picks *which* specialist prompt handles a request.
- Treat the router's output as untrusted: validate the route name, use a confidence threshold, have a fallback, and catch router failures.
- Routers should be small/cheap; specialists can be bigger.

## Day 4 — Controlled experiments

```bash
python -m week3.lesson_04_controlled_experiment 3
```

1. Change **one** thing. Hold model, settings, inputs fixed.
2. Same inputs for every variant.
3. **Repeat** — LLM outputs vary; one run proves nothing.
4. Choose metrics **before** you look at outputs.
5. Report mean **and** spread; decide on pass rate.

## Day 5 — Practical: lesson generator

```bash
python -m week3.lesson_generator "What is an API?"
python -m week3.lesson_generator --batch week3/lesson_generator/topics.txt
python -m pytest tests/test_lesson_generator.py -v      # offline, free
```

```
topic ─▶ PLANNER (JSON) ─▶ verify_plan ─▶ WRITER (Markdown skeleton)
                                              │
              ┌──── REVISER ◀── issues ◀── verify_lesson (code)  ─┐
              │                              └── CRITIC (rubric) ◀┘ only if structure OK
              └──▶ … max 2 revisions ─▶ output/<slug>.md + .report.json
```

What makes it **consistent**:
| Mechanism | Where |
|---|---|
| Fixed skeleton (same headings, same order) | `prompts.WRITER` |
| Plan step → every lesson has 3 objectives, key terms, analogy, exercise | `prompts.PLANNER` |
| Code-enforced rules: sections, 3 objectives, 3 quiz questions, 300–750 words, readability, key terms present | `verify.py` |
| Rubric critic, acted on only when a score < 4 | `pipeline.critique` |
| Versioned prompts in every report | `PROMPT_VERSION` |
| Batch mode table → consistency across topics, measured | `__main__.py` |

---

## ✅ Exercises

1. **Run the batch.** How many pass without revision? Which rule fails most? Fix the *prompt* (not the checker) and bump `PROMPT_VERSION`. Re-run and compare.
2. **New audience.** `--audience "11-year-olds"`. Which thresholds in `verify.py` should depend on audience? Make them configurable.
3. **Experiment.** Using lesson 04's approach, compare `max_revisions=0` vs `2` on 5 topics: pass rate, cost, latency. Is the revision loop worth it?
4. **Cheaper critic.** Run the critic on a smaller model than the writer. Does the pass rate change? (You'll need a second `Assistant`.)
5. **Router accuracy.** Write 15 labelled messages for lesson 03 and measure router accuracy like Week 2 lesson 03.
6. **Read a bad lesson.** Find a lesson that passed all checks but you think is bad. What check is missing? Add it + a test.

**Self-check:**
- Why does the pipeline run code checks *before* the critic?
- What stops the revise loop running forever, and what happens when it gives up?
- Why must router output be validated?
- Your colleague says "prompt B is better, I tried it twice". What do you ask for?
