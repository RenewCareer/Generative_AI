# Track 3: GenAI Application Developer

Build production-grade generative AI applications, from the first API call to a monitored,
containerised service. Each module has a teaching guide, a short slide deck with speaker
notes, runnable lessons, a complete example application, tests, and a lab.

**Prerequisites:** [Track 1](../01-Foundations-and-Orientation/README.md) and
[Track 2](../02-Prompt-Engineering/README.md), or comfortable Python.

## Course map

Every unit builds on the one before it. Together they form one system.

| # | Folder | You learn | You build | Time |
|---|---|---|---|---|
| 01 | [GenAI Application foundations](01_GenAI%20Application%20foundations/README.md) | Tokens, context, attention, API anatomy | Study Buddy CLI | 2.5 h |
| 02 | [LLM Applications Engineering](02_LLM%20Applications%20Engineering/README.md) | Prompts as code, structured output, memory, retries, cost | Feedback Analyzer | 3 h |
| 03.1 | [Data ingestion](03_%20Data%20ingestion%20and%20RAG/01_data%20Ingestion/README.md) | Loaders, validation, quarantine, incremental sync | Knowledge Base Ingestor | 2.5 h |
| 03.2 | [Processing and chunking](03_%20Data%20ingestion%20and%20RAG/02_Document_processing_chunking/README.md) | Extraction, cleaning, chunking strategies | Document Processor | 3 h |
| 03.3 | [Embeddings and vector search](03_%20Data%20ingestion%20and%20RAG/03_embedding_vector_search/README.md) | Cosine similarity, FAISS, ANN, filters | FAQ Search | 2.5 h |
| 03.4 | [Building a RAG application](03_%20Data%20ingestion%20and%20RAG/04_building_rag_application/README.md) | Grounding, citations, refusal | Policy Assistant | 2.5 h |
| 03.5 | [Advanced retrieval and evaluation](03_%20Data%20ingestion%20and%20RAG/05_advnced_retrieval_evaluation/README.md) | BM25, hybrid, reranking, MRR, nDCG | Retrieval Benchmark | 3 h |
| 03.6 | [Production-grade RAG](03_%20Data%20ingestion%20and%20RAG/06_production-grade_RAG/README.md) | Access control, caching, injection, tracing | Production RAG API | 3 h |
| 04 | [Tool calling and AI agents](04_Tool%20Calling%20and%20AI%20Agents/README.md) | Tools, agent loop, guardrails, routing, MCP | Helpdesk Agent | 3.5 h |
| 05 | [Multimodal AI](05_multimodal%20AI/README.md) | Vision, image generation, voice, routing | Expense Assistant | 3 h |
| 06 | [Backend application interfaces](06_Backend%20Application%20interfaces/README.md) | FastAPI, SSE, auth, rate limits, jobs | AI Chat API with web UI | 3 h |
| 07 | [Evaluations, security, reliability](07_Evaluations%20security%20and%20reliability/README.md) | Eval gates, red-teaming, PII, circuit breakers | Guarded Assistant | 3.5 h |
| 08 | [Production deployment and MLOps](08_Production%20deployment%20and%20MLOps%20for%20GenAI/README.md) | Docker, metrics, canary prompts, budgets | Deployable service and capstone | 3.5 h |

## Setup

Run these once, from this folder. The course is tested on Python 3.13. Python 3.14 is not
supported yet, because some dependencies may not have builds for it.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

On macOS or Linux, use `python3.13 -m venv .venv` and `source .venv/bin/activate`.

The `.venv` folder is ignored by git, and it is separate from the older environments inside
the 01 and 03.2 folders. Those can stay.

Then confirm that everything works. This takes about a minute, makes no API calls, and costs nothing:

```powershell
python scripts/check_all.py
```

### Mock mode and real models

**No API key is needed to run this course.** Without a key, the lessons use a clearly labelled
mock provider, and the terminal prints `MOCK MODE`. This keeps a classroom running when keys,
budgets or Wi-Fi are limited, and it makes the tests repeatable.

The mock does not think. It quotes the best-matching sentence, or follows a script written for
that lesson. To see real behaviour, add a key:

```powershell
copy .env.example .env     # then edit .env and add your key
python scripts/live_check.py     # a few very small API calls, which cost a little money
```

Your existing key in `02_LLM Applications Engineering/.env` is not picked up automatically.
Copy it into the new `.env` in this folder. The provider is chosen in this order: `LLM_PROVIDER`,
then an OpenAI key, then an Anthropic key, then the mock.

## How each folder is organised

```
<module>/
  README.md            Teaching guide: outcomes, timing, concepts, walkthrough, lab answers
  presentation.pptx    Short slide deck, with speaker notes on every slide
  lessons/             Small scripts, numbered in teaching order
  project/             The complete example application
  tests/               Run with: python -m pytest tests
```

Your earlier files (`app.py`, `analyze_review.py`, `Data_ingestion.ipynb` and others) are
unchanged, and the guides refer to them. In `02_Document_processing_chunking`, the example
application uses the structure you created there, with the empty files filled in.

Shared code lives in [genai_kit/](genai_kit/). Modules 01 and 02 show the raw provider SDKs, and
later modules reuse the kit, so that each lesson can focus on its own topic. The fictional
**Acme Retail** data in [course_data/](course_data/) is used throughout.

## Teaching a session

1. **Present** the deck (10 to 15 minutes). The speaker notes say which lesson to run at each slide.
2. **Demonstrate** the lessons live, predicting the output before each run.
3. **Walk through** the example application in `project/`.
4. **Lab** (30 to 45 minutes). Answers and marking notes are in each guide.
5. **Debrief** using the "Check for understanding" questions in the guide.

## Rebuilding the slides

The decks are generated, so one design change can restyle all of them. Text can also be edited
directly in PowerPoint, but a rebuild overwrites those edits.

```powershell
cd presentations
npm install
node build_decks.js          # all decks
node build_decks.js 03-02    # one deck
```

Slide content is in `presentations/decks_*.js`, and the templates are in `lib.js`.

## What has been verified

| Check | Status |
|---|---|
| All tests, lessons and example apps, offline | Passing: `python scripts/check_all.py` |
| OpenAI and Anthropic request and response formats | Tested with the real SDKs against fake HTTP servers |
| Chat API over real HTTP, with streaming | Run with uvicorn, using curl and a browser |
| `docker-compose.yml` | Syntax validated with `docker compose config` |
| Slides | Rendered and measured in PowerPoint, with no text overflow |
| **Real model calls** | **Not yet run. Use `python scripts/live_check.py`** |
| **Docker image build** | **Not yet run. Start Docker Desktop, then follow the Module 08 guide** |
| **Image, speech and transcription calls** | Image generation request tested with a fake server. Speech and transcription are **not tested** with a real provider |

---
Back to the [main curriculum](../README.md)
