# Module 03.4: Building a RAG Application

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 2.5 hours | **Next:** [Module 03.5](../05_advnced_retrieval_evaluation/README.md)

## Learning outcomes

By the end, students can:

- Explain why RAG exists, and when another approach is better
- Write a grounded prompt that cites sources and refuses safely
- Verify citations in code, rather than trusting the model
- Debug a bad answer by checking retrieval first

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: why RAG | `presentation.pptx` |
| 25 min | RAG in 30 lines | `lessons/01_rag_in_30_lines.py` |
| 25 min | Grounding and refusal | `lessons/02_grounding_and_refusal.py` |
| 20 min | Citations | `lessons/03_citations_you_can_verify.py` |
| 25 min | Example app | `project/rag.py`, `project/policy_assistant.py` |
| 35 min | Lab | Below |

## Concepts

**The idea.** Do not ask the model to remember your facts. Find the relevant passages, put them in the
prompt, and tell the model to answer only from them.

**Two pipelines.** Indexing runs ahead of time: load, chunk, embed and store. Answering runs on each
request: retrieve, augment, generate and verify. The model never sees your index, only the text you
selected. So if retrieval fails, nothing later can save the answer.

**RAG, or something else?**

| Need | Best tool |
|---|---|
| Answers from documents that change | RAG |
| Totals and aggregates ("sales last month") | SQL |
| Live data ("where is my order?") | An API tool (Module 04) |
| A consistent style or format | Prompting, possibly fine-tuning |

**Layers of trust.**

1. A **score threshold** refuses in code, with no model call, when nothing relevant was found.
2. A **refusal rule** in the prompt covers relevant-looking text that lacks the answer.
3. A **citation check** in code flags sources that do not exist.
4. **Showing the sources** lets users check for themselves.

A citation check confirms that a source exists, not that it supports the claim. Module 03.5 evaluates that.

**The most useful debugging rule.** On a bad answer, first look at what was retrieved. Wrong chunks mean a
retrieval problem. Right chunks mean a generation problem. This one split saves hours.

## Run it

```powershell
python lessons/01_rag_in_30_lines.py
python lessons/02_grounding_and_refusal.py
python lessons/03_citations_you_can_verify.py
python project/policy_assistant.py --question "What is the hotel limit per night?"
python project/policy_assistant.py
python -m pytest tests
```

### What to expect

Offline, the mock quotes the best-matching sentence. It shows the flow, and it does not reason:

```
Hotel stays are reimbursed up to 180 dollars per night. [1]

Sources:
  [1] Travel and Expense Policy (expense_policy#...)
```

Exact source numbers depend on the retrieval order. Mock mode matches words, so it can pick a poor
sentence, or refuse a question a real model would answer. Say this openly, and with a key, try a
question that needs two sources, such as comparing the meal and hotel limits.

## Code walkthrough

| Part of `project/rag.py` | Teaching point |
|---|---|
| `SYSTEM_PROMPT` | Each rule prevents a known failure |
| `REFUSAL` | An exact string can be detected in code and evaluations |
| `build_user_prompt` | RAG is mostly careful string building |
| `ask` | The threshold check avoids a needless model call |
| `invalid_citations` | Checks each `[n]` against what was retrieved |

Note that `min_score` depends on the embedding model. Tune it again whenever the model changes.

## Industry standards

- Cite sources, and let users check them
- Allow "I don't know": it is better than a confident guess
- Limit the context: more chunks cost more, and can reduce quality
- Log retrieval results, so that bad answers can be debugged
- Label AI answers, and offer a route to a person

## Lab

1. Add a policy document with a fact of your own, and confirm that the assistant answers from it.
2. Add a `--debug` flag that prints the retrieved chunks. Find a question that retrieves the wrong one.
3. Warn when an answer has no citation at all.

**Marking notes.** Task 1: add a Markdown file with front matter in `course_data/docs`. This also changes
results in other modules, so remove it afterwards, or the golden set may shift. Task 2: have students bring
their bad retrieval to the next session. Task 3: check `cited` is empty while `refused` is false.

## Check for understanding

1. Why can a model not save an answer after retrieval fails? *It only sees the text you gave it.*
2. Why check citations in code? *Models can invent source numbers.*
3. What does a citation check not prove? *That the source really supports the claim.*
4. When should you not use RAG? *For aggregates and live data.*
