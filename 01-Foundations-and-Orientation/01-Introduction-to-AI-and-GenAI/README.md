# 1.1 Introduction to Artificial Intelligence & Generative AI

## Why this matters

Every later module assumes you can answer, without hesitating: *"what is actually happening when a model 'generates' something?"* If you can't, RAG (Track 3) will feel like magic instead of engineering, and you won't know how to debug it when it breaks. This lesson builds that mental model from first principles before you touch a single API.

## Concepts

**Artificial Intelligence (AI)** is the broad field of building systems that perform tasks we associate with intelligence — reasoning, perception, language, planning. It includes everything from a chess engine's search algorithm to a spam filter to ChatGPT.

**Machine Learning (ML)** is a subset of AI: instead of hand-coding rules, you show the system examples and it learns a function that maps inputs to outputs. A spam filter trained on labeled emails is ML.

**Deep Learning (DL)** is a subset of ML that uses neural networks — layered mathematical functions loosely inspired by neurons — with enough layers ("deep") to learn very complex patterns directly from raw data (pixels, audio, text) instead of hand-engineered features.

**Generative AI (GenAI)** is a subset of deep learning models trained to *produce* new content — text, images, audio, code — rather than just classify or predict a single label. The key distinction:

| | Discriminative model | Generative model |
|---|---|---|
| Question it answers | "Which category does X belong to?" | "What's a plausible continuation/completion of X?" |
| Example | Spam / not-spam classifier | Large Language Model (LLM) writing an email |
| Output | A label or number | New content (text, image, audio...) |

```
AI
└── Machine Learning
    └── Deep Learning
        └── Generative AI   (LLMs, diffusion image models, etc.)
```

### How does a generative *text* model actually generate?

At its core, a modern LLM is a next-token predictor. Given a sequence of tokens (word pieces), it outputs a probability distribution over "what token comes next," samples one, appends it, and repeats. That's it — there's no separate "planning" step hidden inside; the illusion of reasoning emerges from a model trained on enormous amounts of text learning statistical structure well enough to produce coherent, useful continuations.

This one idea — *predict-and-sample, one token at a time* — is the thread connecting a toy Markov chain (example 1 below) to GPT-2 running on your laptop (example 2) to Claude answering your questions through an API (example 3). They differ enormously in scale and quality, not in the fundamental mechanism.

## Step-by-step walkthrough

> 💡 **Prefer Jupyter?** Every script below also has a `.ipynb` notebook of the same name in `examples/`, with the explanation broken into markdown cells between runnable code cells so you can read and run it one step at a time. `01_beginner_rule_based_vs_generative.ipynb` already has its output pre-run and saved, so you can read it before installing anything. Open it with `jupyter notebook` / `jupyter lab`, or directly in VS Code / Cursor if you have the Jupyter extension.

1. **Read the concepts above twice.** Make sure you can draw the AI → ML → DL → GenAI nesting diagram from memory.
2. **Run `examples/01_beginner_rule_based_vs_generative.py`.** No installs needed — pure Python. It contrasts a rule-based ("classic AI") chatbot with a simple statistical Markov-chain text generator, so you *see* the difference between hard-coded logic and next-token prediction before any ML library is involved.
3. **Set up a virtual environment and install dependencies for example 2:**
   ```bash
   cd 01-Foundations-and-Orientation/01-Introduction-to-AI-and-GenAI/examples
   pip install -r requirements.txt
   ```
   This installs `transformers` and `torch` — expect a multi-minute, multi-GB download the first time. If you're on a low-bandwidth connection or short on disk space, read the script instead of running it, then come back to it later.
4. **Run `02_intermediate_local_transformer_generation.py`.** It loads a real (small) generative language model, GPT-2, entirely on your machine — no API key, no internet call at inference time — and generates text. Read the comments; notice the model produces *fluent but often factually wrong* text. That's expected and important: GPT-2 has no grounding in facts, only in patterns of language.
5. **Get an Anthropic API key** (console.anthropic.com) and set it as an environment variable:
   ```bash
   # macOS/Linux
   export ANTHROPIC_API_KEY="your-key-here"
   # Windows PowerShell
   $env:ANTHROPIC_API_KEY = "your-key-here"
   ```
6. **Run `03_advanced_api_generation_and_comparison.py`.** It calls a frontier model (Claude) through the real Anthropic API and prints a side-by-side comparison against the local GPT-2 output from step 4 — same prompt, wildly different quality. This is the gap that the rest of this curriculum exists to help you close: knowing *when* you need frontier-model quality vs. when a small local model is enough.

### Try it yourself

- Modify the Markov chain in example 1 to use a 3-word window instead of 2. Does the output get more or less coherent? Why?
- Change the `prompt` in example 2 and 3 to the same creative-writing prompt (e.g. "Write the opening line of a mystery novel set in a lighthouse"). Compare quality side by side.
- In example 3, change `temperature`-equivalent behavior by asking Claude the same question 3 times and comparing variation in the answers (see the script's comments on why LLM output isn't perfectly deterministic).

## Sub-topic recap

You should now be able to explain: AI vs ML vs DL vs GenAI as nested categories; discriminative vs generative models; and "next-token prediction" as the mechanical core of text generation, regardless of model size or quality.

---
⬅️ Back to [Track 1 overview](../README.md)
