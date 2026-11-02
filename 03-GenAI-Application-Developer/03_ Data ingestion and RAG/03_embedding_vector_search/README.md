# Module 03.3: Embeddings and Vector Search

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 2.5 hours | **Next:** [Module 03.4](../04_building_rag_application/README.md)

## Learning outcomes

By the end, students can:

- Explain embeddings and cosine similarity from first principles
- Compare exact and approximate indexes using measured results
- Build a persistent search engine with metadata filters
- Choose where vectors should live, for a given situation

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides, and arrows on the whiteboard | `presentation.pptx` |
| 25 min | Embedding intuition | `lessons/01_embedding_intuition.py` |
| 30 min | Exact against approximate | `lessons/02_exact_vs_approximate.py` |
| 15 min | Metadata filters | `lessons/03_metadata_filtering.py` |
| 25 min | Example app | `project/faq_search.py` |
| 30 min | Lab | Below |

## Concepts

**Embeddings.** An embedding model turns text into a list of numbers, trained so that similar meanings
land close together. "Money back" and "refund" share no words, but they should be close.

**Cosine similarity** measures the angle between two vectors: 1 is the same direction, and 0 is
unrelated. With normalised vectors, it equals the inner product, which is why the code uses `IndexFlatIP`.

**Offline mode has a real limit, and it teaches something.** Without a key, `HashingEmbedder` compares
shared words, not meaning. Lesson 1 shows the failure on purpose: for "How do I get my money back?", it
ranks a sentence about money orders first, and the refund sentence gets 0.000. Add an OpenAI key to see
a real embedding model handle this. Anthropic has no embeddings endpoint, so Claude users need an
OpenAI key, or another embedding provider, for this part.

**Exact and approximate search.**

| Index | How it works | Tune with | Note |
|---|---|---|---|
| Flat | Compares every vector | Nothing | Always exact |
| IVF | Searches the nearest clusters | `nprobe` | Needs training |
| HNSW | Navigates a layered graph | `efSearch` | Uses more memory |

**Recall** measures what approximate search gave up: of the true top 10, how many did it return?

**Where vectors live.**

| Option | A good fit when |
|---|---|
| FAISS | Learning, or static data inside one process |
| pgvector | You already run Postgres, and want SQL filters and joins |
| Chroma, Qdrant, Weaviate | You want a dedicated open-source vector database |
| Pinecone and managed services | You would rather not operate the infrastructure |

Features and prices change, so check them with each vendor. `FaissStore` has a small interface (`build`,
`search`, `save`, `load`), so moving to another store touches little code.

## Run it

```powershell
python lessons/01_embedding_intuition.py
python lessons/02_exact_vs_approximate.py
python lessons/03_metadata_filtering.py
python project/faq_search.py build
python project/faq_search.py search "how long is the warranty"
python project/faq_search.py search "annual leave" --access internal
python -m pytest tests
```

### What to expect

From `lessons/02_exact_vs_approximate.py`, measured on one laptop. Your numbers will differ:

```
index                      build    per query    recall       memory
Flat (exact)               0.01s      0.529ms    100.0%        26 MB
IVF nprobe=1               0.73s      0.015ms     94.6%        26 MB
IVF nprobe=10              0.75s      0.045ms    100.0%        26 MB
HNSW efSearch=16           1.22s      0.012ms     96.1%        39 MB
HNSW efSearch=64           1.15s      0.020ms     98.3%        39 MB
```

The synthetic data clusters tightly, so real-world recall may be lower. Measure on your own vectors.

## Code walkthrough: FAQ Search

| Part of `project/faq_search.py` | Teaching point |
|---|---|
| `IndexFlatIP` | Inner product on normalised vectors is cosine |
| `OVERFETCH` | FAISS has no metadata filter here, so fetch extra, and filter afterwards |
| `save` | Uses `serialize_index`, so that paths with spaces work on Windows |
| `meta.json` | Records the embedding model |
| `load` | Refuses a different model, rather than returning meaningless results |

## Industry standards

- One embedding model per index, with its name stored
- Keep the original text, so that you can re-embed with a better model later
- Filter in retrieval, for access and tenant rules
- Measure recall for any approximate index
- Embed in batches, and handle rate limits

## Lab

1. Change the vector count in lesson 2 to 200,000. Which index would you choose now?
2. Add a `--department` filter to `faq_search.py`, and test it with an HR question.
3. With an API key, rebuild using real embeddings, and compare results for "How do I get my money back?"

**Marking notes.** Task 1: exact search slows roughly in line with the vector count, while approximate
indexes grow more slowly but take longer to build. Task 2: follow the `access` pattern, and make sure
the over-fetch still finds rare matches. Task 3: the build must be re-run, because `load` refuses
the old index. That refusal is a good moment to show.

## Check for understanding

1. Can you compare vectors from two different models? *No. They live in different spaces.*
2. Is a similarity of 0.3 good? *It depends on the model, so thresholds must be tuned for each one.*
3. Why start with exact search? *It is simple, always correct, and often fast enough.*
4. Why not hide restricted documents using the prompt? *An instruction is not a security control. The text should never be retrieved.*
