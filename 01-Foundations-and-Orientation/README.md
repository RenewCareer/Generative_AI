# 🧭 Track 1 — Foundations & Orientation

Welcome — this is where every GenAI career path starts, regardless of whether you end up as a prompt engineer, application developer, product manager, or infrastructure engineer. You cannot skip this track and expect the later ones to make sense: RAG (Track 3) needs the math intuition from 1.4, every API example needs the Python patterns from 1.3, and every prompting technique in Track 2 needs the mental model of "how generation actually works" from 1.1.

## Why this track matters

Generative AI moves fast, and it's easy to start "prompting ChatGPT" without ever understanding *what's actually happening* underneath. That gap shows up later as: not knowing why a prompt fails, not knowing why RAG retrieval returns garbage, not knowing why a model hallucinates, and not knowing how to reason about cost/latency/quality tradeoffs. This track closes that gap deliberately, in five steps.

## Sub-topics (work through in order)

| # | Sub-topic | You'll be able to... |
|---|-----------|----------------------|
| 1.1 | [Introduction to AI & Generative AI](01-Introduction-to-AI-and-GenAI/README.md) | Explain the difference between AI, ML, DL, and GenAI, and how generative models actually generate. |
| 1.2 | [AI Landscape and Industry Use Cases](02-AI-Landscape-and-Industry-Use-Cases/README.md) | Map GenAI capabilities to real business problems across industries, and speak the vocabulary of the field. |
| 1.3 | [Python Refresher for AI](03-Python-Refresher-for-AI/README.md) | Write the Python patterns (data handling, API calls, classes) used in every later track. |
| 1.4 | [Math and Statistics Essentials](04-Math-and-Statistics-Essentials/README.md) | Understand vectors/embeddings, probability over tokens, and how models learn via gradient descent. |
| 1.5 | [Responsible and Ethical AI](05-Responsible-and-Ethical-AI/README.md) | Identify bias, hallucination, and privacy risks, and build basic automated guardrails. |

## Step-by-step: how to work through this track

1. **Set up your environment once, for the whole track.**
   ```bash
   cd 01-Foundations-and-Orientation
   python -m venv .venv
   # macOS/Linux:
   source .venv/bin/activate
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   ```
   Each sub-topic's `examples/` folder has its own `requirements.txt`. Install per sub-topic as you reach it — don't install everything up front, so you understand what each concept actually depends on.

2. **Open `01-Introduction-to-AI-and-GenAI/README.md` and read it fully before touching code.** Concepts first, code second — that order is intentional throughout this curriculum.

3. **Run the examples in numeric order** inside each sub-topic's `examples/` folder:
   - `01_beginner_*` — no/minimal dependencies, builds intuition from first principles.
   - `02_intermediate_*` — introduces a real library or a slightly harder concept.
   - `03_advanced_*` — combines ideas, closer to how you'd actually use this on the job.

4. **Do the "Try it yourself" exercise at the end of each sub-topic README.** This is not optional — reading code and writing code build different muscles, and the later tracks assume you've built the second one.

5. **Move to sub-topic 1.2 only once you can explain 1.1 in your own words**, out loud, without looking at the README. Repeat for each sub-topic. This "explain it back" checkpoint is the fastest way to catch a concept you only think you understood.

6. When all five sub-topics are done, you're ready for [Track 2 — Prompt Engineer](../02-Prompt-Engineering/README.md).

## What you need before starting

- Python 3.10+ installed and runnable from your terminal (`python --version`)
- No API keys required for this track — everything runs locally or with free/local models, by design, so you can start today.

---
⬅️ Back to [main curriculum](../README.md)
