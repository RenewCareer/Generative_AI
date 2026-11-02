# Module 03.6: Production-Grade RAG

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 04](../../04_Tool%20Calling%20and%20AI%20Agents/README.md)

## Learning outcomes

By the end, students can:

- Enforce access control in retrieval, so that nothing leaks through the prompt
- Explain and defend against indirect prompt injection
- Cache answers without leaking data or serving stale answers
- Trace each request, swap indexes with no downtime, and degrade gracefully

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: the layered request | `presentation.pptx` |
| 20 min | Access control | `lessons/01_access_control.py` |
| 25 min | Semantic cache and re-indexing | `lessons/02_semantic_cache.py` |
| 25 min | Indirect prompt injection | `lessons/03_indirect_prompt_injection.py` |
| 20 min | Tracing and fallback | `lessons/04_tracing_and_fallback.py` |
| 20 min | The API | `project/service.py` |
| 45 min | Lab | Below |

## Concepts

**Access control belongs in retrieval.** "Do not reveal HR documents" in a prompt is not a security
control, since the text still reaches the model. Filtering in retrieval means that forbidden text is never
fetched, and the model cannot leak what it never saw.

**Semantic cache.** Reuse an answer when a new question is close to an earlier one. It has two risks:

- **Leaks:** a shared cache could serve an employee's answer to a customer. So each entry is scoped by role.
- **Staleness:** the scope also includes the index version, so that a re-index invalidates old answers.

Too low a threshold is dangerous, because different questions start sharing an answer.

**Indirect prompt injection.** A document can contain instructions aimed at your assistant. Screening catches
known phrasings, and a rephrased attack gets through. The lesson shows both on purpose. Real defence is
layered: control what gets ingested, mark sources as untrusted, check outputs, and limit permissions.

**Blue/green re-indexing.** Build the new index on the side, then switch in one step. A request in progress keeps
its snapshot. With a hosted database, the same idea is writing a new collection and switching an alias.

**Tracing.** One record per request: what ran, how long it took, and what it decided. Tools such as Langfuse,
LangSmith and Arize Phoenix collect this kind of data, and OpenTelemetry is the common standard.

**Fallback ladder.** Primary model, then a backup model, then the source passages, then a clear message.

## Run it

```powershell
python lessons/01_access_control.py
python lessons/02_semantic_cache.py
python lessons/03_indirect_prompt_injection.py
python lessons/04_tracing_and_fallback.py
python -m pytest tests
python -m uvicorn project.service:app --port 8010
```

Then open http://localhost:8010/docs, and try `/v1/ask` with `X-Role` set to `employee`, then `customer`.

### What to expect

```
Role: employee
  answer : Full-time employees receive 24 days of paid annual leave each year. [1]
Role: customer
  answer : I don't know based on the provided documents.
```

From the injection lesson, where the scripted model deliberately obeys whatever it reads:

```
WITHOUT SCREENING (plain RAG)
  answer: Please send your card number to refunds@evil.example to receive your refund.
WITH SCREENING (ProductionRag)
  chunks blocked: 1
  answer: Customers may return most items within 30 days of delivery for a full refund. [1]
```

## Code walkthrough

| Part | Teaching point |
|---|---|
| `components.access_filter` | The rule, enforced before generation |
| `components.SemanticCache` | Scope, threshold and expiry |
| `pipeline.IndexSnapshot` | Immutable, so that swaps are safe |
| `pipeline.ProductionRag.ask` | The whole layered flow, in one readable method |
| `pipeline._generate` | The fallback order |
| `service.create_app` | The app takes its pipeline as an argument, which makes it testable |

**Important limitation.** The API reads the role from an `X-Role` header. That keeps the demo simple, and it is
insecure: a real service takes the role from a verified token. The code comment says so, and Module 06
covers authentication.

## Industry standards

- Permission-aware retrieval, per user, at query time
- A trace for each request, and OpenTelemetry for portability
- Versioned indexes, with atomic swaps and rollback
- Caches scoped by permissions and data version
- The OWASP Top 10 for LLM Applications as a review checklist

## Lab

1. Add a `finance` role that may read only finance and public documents. Prove it with a test.
2. Write a poisoned document that gets past the screen, then add a defence that catches it.
3. Add a time limit, and return the degraded answer if generation is too slow.

**Marking notes.** Task 1: `ROLE_ACCESS` works by access level, so this needs a filter on `department` as well.
This is a good design discussion. Task 2 works well as a contest between pairs. An output check for unexpected
email addresses or links is one good answer. Task 3: use a `concurrent.futures` timeout, and note that the
provider call keeps running in the background unless it is cancelled.

## Check for understanding

1. Why is a prompt instruction not access control? *The text still reaches the model, and clever input can extract it.*
2. How can a cache become a data breach? *By serving one user's permitted answer to another user.*
3. What happens to cached answers after a re-index? *The version is in the scope, so they stop matching.*
4. Should degraded answers be cached? *No. The next request deserves a fresh chance.*
