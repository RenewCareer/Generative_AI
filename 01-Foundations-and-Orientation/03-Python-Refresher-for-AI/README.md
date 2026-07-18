# 1.3 Python Refresher for AI

## Why this matters

Every script in this curriculum — from a Markov chain to a RAG pipeline — is built out of the same handful of Python patterns: data structures, comprehensions, functions/classes, and calling external APIs safely. If those patterns aren't automatic for you yet, later tracks will feel like they're teaching two things at once (the AI concept *and* the Python). This lesson makes the Python automatic first.

## Concepts

This isn't a full Python course — it assumes you know basic syntax (variables, `if`, `for`). It refreshes and sharpens the specific patterns AI/GenAI work leans on constantly:

- **Data structures for data wrangling** — lists, dicts, tuples, sets, and *comprehensions* (a compact way to build a list/dict from a loop) — because you'll constantly be reshaping API responses, dataset rows, and embeddings.
- **Functions and classes as reusable units** — you'll write a "call the LLM" function or class exactly once and reuse it everywhere, rather than copy-pasting an API call in every script.
- **NumPy arrays and pandas DataFrames** — the standard way numeric and tabular data is represented in Python's data/AI ecosystem. Embeddings are NumPy arrays under the hood; datasets are usually pandas DataFrames.
- **Environment variables and `.env` config** — API keys should never be hard-coded into a script. You'll learn the standard pattern for keeping secrets out of your code.
- **Retries and error handling for network calls** — API calls fail sometimes (rate limits, timeouts, transient network errors). Production AI code always wraps calls in retry logic instead of crashing on the first hiccup.

## Step-by-step walkthrough

> 💡 **Prefer Jupyter?** Every script below also has a `.ipynb` notebook of the same name in `examples/`, with the explanation broken into markdown cells between runnable code cells. Notebooks 1 and 2 are already executed and saved, so you can read the real output before installing anything. Open with `jupyter notebook` / `jupyter lab`, or directly in VS Code / Cursor with the Jupyter extension.

1. **Set up your environment for this sub-topic:**
   ```bash
   cd 01-Foundations-and-Orientation/03-Python-Refresher-for-AI/examples
   pip install -r requirements.txt
   ```
2. **Run `01_beginner_python_fundamentals.py`.** No AI content here at all — it's a drill of list/dict comprehensions, `*args`/`**kwargs`, unpacking, and simple classes, using small text-processing examples (word counts, filtering) that mirror what you'll do to data in later modules.
3. **Run `02_intermediate_numpy_pandas_for_ai.py`.** It introduces NumPy vectors (and previews *why* they matter: embeddings — dense numeric representations of meaning — are just NumPy arrays, a concept you'll build real intuition for in sub-topic 1.4) and pandas DataFrame operations (filtering, grouping, joining) using a small synthetic dataset of "documents."
4. **Run `03_advanced_llm_client_utility.py`.** This is the most important script in this sub-topic: it builds a small, reusable `LLMClient` class around the Anthropic API with environment-variable configuration, input validation, and automatic retry-with-backoff on transient failures. This exact pattern — a thin, well-tested wrapper class around an LLM API call — is what you'll extend throughout Track 2 and Track 3. Requires `ANTHROPIC_API_KEY` to be set (see sub-topic 1.1's README for how).

### Try it yourself

- In script 1, write a new function `top_n_words(text, n)` that returns the `n` most frequent words in a string, using a dict comprehension plus `sorted()`.
- In script 2, add a new column to the DataFrame that's the ratio of two existing numeric columns, using vectorized pandas operations (no `for` loop).
- In script 3, add a `max_tokens` parameter to `LLMClient.ask()` with a sensible default, and add a unit-style check (a simple `assert`) confirming the client raises a clear error when `ANTHROPIC_API_KEY` isn't set.

## Sub-topic recap

You should now be comfortable with comprehensions, functions/classes as reuse boundaries, NumPy/pandas basics, and — critically — the "config via environment variable + retry wrapper" pattern that every production LLM integration uses.

---
⬅️ Back to [Track 1 overview](../README.md)
