# Module 03.5: Advanced Retrieval and Evaluation

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 03.6](../06_production-grade_RAG/README.md)

## Learning outcomes

By the end, students can:

- Combine keyword and vector search with reciprocal rank fusion
- Decide when reranking and query rewriting earn their cost
- Calculate hit rate, MRR and nDCG by hand
- Evaluate generated answers, and understand each method's limits

## Session plan

| Time | Activity | Material |
|---|---|---|
| 10 min | Review last session's bad retrievals | Student examples |
| 15 min | Slides | `presentation.pptx` |
| 25 min | Keyword, vector and hybrid | `lessons/01_keyword_vs_vector.py` |
| 25 min | Rerank and rewrite | `lessons/02_rerank_and_query_rewrite.py` |
| 25 min | Retrieval metrics, on the board | `lessons/03_retrieval_metrics.py` |
| 25 min | Answer evaluation | `lessons/04_answer_evaluation.py` |
| 15 min | The benchmark | `project/benchmark.py` |
| 40 min | Lab | Below |

## Concepts

**BM25** is keyword search that weighs rare terms more, and it is excellent for codes like `SHP-404`.
Vector search handles meaning. They fail differently, which is why combining them works.

**Reciprocal rank fusion** merges ranked lists using ranks alone, so that different score scales do not
matter. `score = sum of 1 / (60 + rank)`. A chunk at rank 1 and rank 3 scores `1/61 + 1/63 = 0.0323`.

**Reranking.** Fetch many candidates cheaply, then rescore them with a slower, sharper model, such as a
cross-encoder or a rerank API. Offline, the course uses a simple term-proximity heuristic, so the lesson
shows the flow, and not the real quality gain.

**Query rewriting.** Ask a model for alternative phrasings, to bridge the vocabulary gap. Offline, the
rewrites are scripted.

**Retrieval metrics.** Worked example, for a relevant document at rank 3:

| Metric | Question it answers | Value |
|---|---|---|
| hit@3 | Was it in the top 3? | 1.00 |
| hit@1 | Was it first? | 0.00 |
| MRR | How early? 1 / rank | 0.33 |
| nDCG@3 | Rank-discounted score, 1.0 is perfect | 0.50 |

**Evaluating answers.** Layer the methods:

| Method | Strength | Limit |
|---|---|---|
| Exact fact check | Cheap and strict | Needs known answers |
| Groundedness (word overlap) | Cheap, catches blatant invention | Misses a wrong number |
| LLM judge | Handles paraphrase | Costs money, and can be wrong |
| Human review | The source of truth | Slow |

Frameworks such as Ragas and DeepEval provide metrics like these. Students should understand what they
compute. Metrics here are written by hand in `project/metrics.py`, so that nothing is hidden.

## Run it

```powershell
python lessons/01_keyword_vs_vector.py
python lessons/02_rerank_and_query_rewrite.py
python lessons/03_retrieval_metrics.py
python lessons/04_answer_evaluation.py
python project/benchmark.py
python -m pytest tests
```

### What to expect

`project/benchmark.py`, offline, on the paraphrased questions:

| Retriever | hit@1 | hit@5 | MRR | nDCG@5 | Answer in top 3 |
|---|---|---|---|---|---|
| Vector | 0.25 | 0.75 | 0.44 | 0.52 | 0.38 |
| BM25 | 0.50 | 0.62 | 0.56 | 0.58 | 0.25 |
| Hybrid (RRF) | 0.50 | 0.75 | 0.59 | 0.63 | 0.38 |
| Hybrid + rerank | 0.50 | 0.75 | 0.59 | 0.63 | 0.38 |

**Read this with care.** The offline "vector" search only sees shared words, so it is weak here, and the
heuristic reranker adds nothing. Real embeddings and a real reranker may change this table, so rerun
it with a key.

On the golden and hard question sets, every strategy scored 1.00, because those questions share words with the
documents. That is a lesson in itself: an easy test set tells you nothing. The first version of this
benchmark had only those sets, and showed no differences until the paraphrased set was added.

## Code walkthrough

| File | Teaching point |
|---|---|
| `project/metrics.py` | Each metric is a few readable lines |
| `project/retrievers.py` | One signature, `(question, k)`, so strategies are easy to compare |
| `project/benchmark.py` | Hard and paraphrased questions, and a report for pull requests |

## Industry standards

- A golden dataset in version control, reviewed by subject matter experts
- Include hard cases: paraphrases, typos, codes, and unanswerable questions
- Evaluate retrieval and generation separately, to find the real cause
- Compare every change with a baseline on the same data
- Turn each production failure into a new test case
- Report cost and latency alongside quality

## Lab

1. Add 5 hard questions to the paraphrased set, and record the baseline.
2. Change one thing, such as chunk size, `k`, or the RRF constant, and rerun.
3. Write a short pull request description: what changed, the numbers, and your decision.

**Marking notes.** The third task is the real exercise. Concluding that a change did not help is a good result,
as long as it is backed by numbers. Watch for students changing two things at once.

## Check for understanding

1. Why does RRF use ranks rather than scores? *BM25 and cosine scores use different scales.*
2. Two systems have equal hit@5, but one has a higher MRR. Which is better? *The higher MRR, since it finds the answer earlier, which allows a smaller k and lower cost.*
3. Why can groundedness be 1.00 on a wrong answer? *Word overlap ignores that "250" differs from "180", if the other words match.*
4. Should you add a reranker by default? *Only if your benchmark shows that it helps enough to justify the cost and latency.*
