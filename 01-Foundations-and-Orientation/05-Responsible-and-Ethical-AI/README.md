# 1.5 Responsible and Ethical AI

## Why this matters

Every track after this one teaches you to *build* with GenAI. This lesson teaches you to build *responsibly* — because the failure modes of GenAI systems (bias, hallucination, privacy leakage) aren't rare edge cases, they're default behaviors of the technology that you have to actively guard against. A developer who ships a RAG app without ever thinking about these risks isn't behind on a "nice to have" — they're missing a core competency the rest of the industry expects. This lesson is deliberately hands-on: you'll write actual detection code, not just read a policy document.

## Concepts

**Bias** — GenAI models are trained on large amounts of human-written text, which contains the biases (gendered language, age discrimination, cultural assumptions) present in that text. A model can reproduce or amplify those biases in its output — e.g. generating job descriptions that subtly discourage certain applicants — without anyone intending it to.

**Hallucination** — LLMs generate the *most statistically plausible* continuation of a prompt, not necessarily the *true* one. When a model states a specific fact — a date, a statistic, a citation — with complete fluency and confidence, that fluency is not evidence of correctness. This is arguably the single most important failure mode to internalize before Track 3 (RAG exists largely to reduce hallucination by grounding answers in retrieved, verifiable text).

**Privacy and PII (Personally Identifiable Information)** — GenAI applications often process or generate text containing emails, phone numbers, names, or other sensitive data. Both directions matter: a model might leak PII it saw during training, and your *application* might carelessly log or forward PII a user typed in.

**Transparency and human-in-the-loop** — Responsible deployment means users know they're interacting with AI, understand its limitations, and have a path to a human when the stakes are high (medical, legal, financial decisions).

**Regulation (context, not memorization)** — Frameworks like the EU AI Act and various US state-level AI laws are pushing risk-based obligations onto AI system builders (documentation, human oversight, transparency to users). You don't need to memorize specific clauses at this stage — you need to know these frameworks exist and generally require exactly the practices this lesson teaches: bias awareness, hallucination mitigation, and privacy protection.

## Step-by-step walkthrough

> 💡 **Prefer Jupyter?** Every script below also has a `.ipynb` notebook of the same name in `examples/`, with the explanation broken into markdown cells between runnable code cells. Notebooks 1 and 2 are already executed and saved, so you can read the real output before installing anything. Open with `jupyter notebook` / `jupyter lab`, or directly in VS Code / Cursor with the Jupyter extension.

1. **Read the concepts above.** For each one, think of a real product you've used (a chatbot, a writing assistant, a search engine) and ask "how would this failure mode show up here?"
2. **Run `examples/01_beginner_bias_keyword_flagging.py`.** No dependencies — pure Python. It scans a small set of sample job postings for common biased/exclusionary language patterns (gendered terms, age-coded phrases, ableist language) and suggests neutral alternatives. This is a simplified version of a real technique: automated bias-linting of AI-assisted or AI-generated content before it ships.
3. **Run `examples/02_intermediate_hallucination_detection.py`.** No dependencies — pure Python (`re` module only). It takes a set of factual claims (simulating "what an LLM said"), extracts the specific factual assertions each one makes, and checks them against a small trusted knowledge base — flagging any claim that doesn't match as a potential hallucination. This is the conceptual core of fact-checking / grounding, which Track 3's RAG systems automate at scale.
4. **Get your Anthropic API key ready** (same as sub-topics 1.1 and 1.3 — set `ANTHROPIC_API_KEY`).
   ```bash
   cd 01-Foundations-and-Orientation/05-Responsible-and-Ethical-AI/examples
   pip install -r requirements.txt
   ```
5. **Run `examples/03_advanced_responsible_ai_pipeline.py`.** This combines everything: it sends a real prompt to Claude, then runs the response through three automated checks — a bias/loaded-language scan, a PII detector (regex for emails/phone numbers), and a hallucination heuristic against a small trusted knowledge base — and prints a "Responsible AI Report" summarizing what it found. This is a miniature version of the kind of automated guardrail pipeline real GenAI applications run on every model output before showing it to a user.

### Try it yourself

- In script 1, add 3 more biased phrases to the flagged-terms dictionary (research a couple of real examples of biased job-posting language) and re-run it against the sample postings.
- In script 2, add a new claim that's subtly wrong (e.g. a fact with the right structure but a wrong number) and confirm the script catches it.
- In script 3, change the prompt sent to Claude to something likely to mention a fact your knowledge base doesn't cover, and observe how the pipeline handles a claim it has no ground truth for (this is an important limitation to notice: absence from the knowledge base isn't proof of hallucination — it's a "cannot verify" case, and good guardrail systems distinguish the two).

## Sub-topic recap

You should now be able to name the major GenAI risk categories (bias, hallucination, privacy, lack of transparency), explain *why* each one happens mechanically (not just that it happens), and have hands-on experience writing simple automated checks for each — a skill you'll build on heavily in Track 4 (Product Manager, for evaluation/governance) and Track 5 (Infrastructure Engineer, for production guardrails).

---
⬅️ Back to [Track 1 overview](../README.md)

🎉 **This completes Track 1 — Foundations & Orientation.** You're ready for [Track 2 — Prompt Engineer](../../02-Prompt-Engineering/README.md).
