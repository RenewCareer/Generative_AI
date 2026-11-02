# Module 02: LLM Applications Engineering

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 03.1](../03_%20Data%20ingestion%20and%20RAG/01_data%20Ingestion/README.md)

## Learning outcomes

By the end, students can:

- Manage prompts as versioned, testable templates
- Get validated structured data from a model, and recover from bad output
- Add streaming and bounded conversation memory
- Handle temporary failures with backoff, and enforce a spending limit

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides, and review the earlier apps | `presentation.pptx`, `app.py`, `app3.py`, `app_history.py` |
| 25 min | Prompts as code | `lessons/01_prompt_templates.py` |
| 30 min | Structured output and repair | `lessons/02_structured_output.py`, `analyze_review.py` |
| 20 min | Streaming and memory | `lessons/03_streaming_and_memory.py` |
| 20 min | Retries and cost | `lessons/04_reliability_and_cost.py` |
| 20 min | Example app walkthrough | `project/review_analyzer.py` |
| 40 min | Lab | Below |

## Concepts

**Prompts are code.** They change behaviour, so version them. A clear prompt states the role, the
rules, and the output format, and it uses delimiters to separate instructions from untrusted data.
Log the prompt version with each result, so that you can answer "what changed?".

**Structured output.** Software cannot branch on a paragraph. Define the shape with Pydantic, and
pass it to the API. A schema guarantees format, not truth: valid JSON can still hold a wrong value.
Business rules need validators, and accuracy needs evaluation (Module 07).

**The repair loop.** If validation fails, send the error back to the model, and let it try again, a
limited number of times. Use it for rules that a schema cannot express.

**Streaming** does not make the model faster. It shows the first words sooner, which makes waiting
feel far shorter.

**Memory.** Every turn resends the history, so it must be bounded. Options are a sliding window (the
lesson), summaries, a long-term fact store, or provider-side state as in `app_history.py`.

**Reliability.** Retry temporary errors (429, 5xx) with exponential backoff and random jitter. Do not
retry permanent errors (400, 401): they will not improve. Provider SDKs retry for you, so set
`max_retries` and `timeout`, and use this pattern around your own multi-step workflows.

## Run it

```powershell
python lessons/01_prompt_templates.py
python lessons/02_structured_output.py
python lessons/03_streaming_and_memory.py
python lessons/04_reliability_and_cost.py
python project/review_analyzer.py
python -m pytest tests
```

Your earlier scripts (`app.py`, `app2.py`, `app3.py`, `app_history.py`, `analyze_review.py`,
`claude_example.py`) call the SDKs directly, and they need a key in this folder's `.env`.

### What to expect

```
Repair loop:
  attempt 1: rejected, 1 error(s) fed back to the model
  attempt 2: rejected, 1 error(s) fed back to the model
  attempt 3: valid
```

`review_analyzer.py` prints one line per review and a summary: for the sample data, 2 positive,
3 negative and 1 neutral. In mock mode, those labels come from keyword matching.

## Code walkthrough: Feedback Analyzer

| Part of `project/review_analyzer.py` | Teaching point |
|---|---|
| `ReviewAnalysis` | Enums make results safe to count and route |
| `PROMPT_VERSION` | Saved with every result, for traceability |
| `<review>` delimiters | Mark the review as data, not instructions |
| `process_row` | One bad row is recorded, and the batch continues |
| `ThreadPoolExecutor` | Parallel calls, with results kept in order |

## Bug hunt

`analyze_review.py` contains a real bug to find together. The function accepts `review_text`, but its
body uses `review`. It works as a script only because a global variable of that name exists, and it
fails when the function is imported. Finding this shows why testing imported code catches bugs that
running a script does not. The file is left unchanged on purpose.

## Industry standards

- Schema-first output, with validation at the boundary
- Semantic versions for prompts, logged on each call
- Backoff with jitter, for temporary errors only
- Per-job budgets that stop automatically
- A thin provider abstraction: see [genai_kit/llm.py](../genai_kit/llm.py)

## Lab

1. Add an `urgency` field (low, medium, high) to the schema, and update the mock.
2. Add a `CostLedger` with a budget, so that the batch stops itself before overspending.
3. Fix the `review` and `review_text` bug, and write a test that would have caught it.

**Marking notes.** Task 1: use `Literal`, and bump `PROMPT_VERSION`. Task 2: the ledger must be
thread-safe if workers share it, which is a good discussion point. Task 3: the test imports
`analyze_review` and passes text in. In a test, patch the module's `client`, since importing the file
reads `config.py`, which needs `OPENAI_API_KEY` to be set.

## Check for understanding

1. Does a JSON schema guarantee that the content is correct? *No, only the shape.*
2. Why add jitter to backoff? *Otherwise many clients retry at the same moment, and overload the service again.*
3. Should a 401 be retried? *No. A bad key does not fix itself.*
4. What does logging the prompt version let you do? *Trace a change in quality back to its cause.*
