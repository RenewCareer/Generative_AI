# 1.2 AI Landscape and Industry Use Cases

## Why this matters

You cannot pitch, build, or evaluate a GenAI solution without knowing the vocabulary and the map of the field: who the major model providers are, what "modality" means, and — most importantly — which business problems GenAI is actually good at solving versus which ones it's a poor (or risky) fit for. This lesson builds that map, then has you write code that queries and reasons over it, because reading a list of use cases and being able to *programmatically reason* about them are different skills.

## Concepts

### The major players (as of this writing)

| Category | Companies / Products |
|---|---|
| Frontier model labs | Anthropic (Claude), OpenAI (GPT), Google (Gemini), Meta (Llama, open-weight) |
| Cloud hyperscalers offering GenAI | Microsoft Azure (Azure OpenAI Service), AWS (Bedrock), Google Cloud (Vertex AI) |
| Vector databases / infra | Pinecone, Weaviate, Qdrant, FAISS (library, not a hosted DB), Chroma |
| Application/orchestration frameworks | LangChain, LlamaIndex |

### Modalities — what kind of content a GenAI system produces

- **Text** — chat, summarization, drafting, classification, code generation
- **Image** — generation (text-to-image), editing, understanding (vision)
- **Audio** — speech-to-text, text-to-speech, music generation
- **Video** — generation and editing (newest, least mature modality)
- **Multimodal** — models that accept and/or produce more than one modality in the same request (e.g. "look at this image and describe it in text")

### Mapping industries to use cases

The same underlying capability (e.g. "summarize a long document") shows up differently across industries:

| Industry | Example GenAI use case |
|---|---|
| Healthcare | Summarizing clinical notes; drafting patient communication |
| Finance | Extracting data from financial filings; fraud-pattern narrative analysis |
| Legal | Contract review and clause extraction; case-law summarization |
| Retail / E-commerce | Personalized product descriptions; customer service chatbots |
| Software/Engineering | Code generation, code review, test generation |
| Marketing | Ad copy generation; campaign personalization at scale |
| Education | Personalized tutoring; auto-generated practice questions |

### Build vs. buy

A recurring decision in industry: do you call a hosted frontier model API (fast to ship, ongoing cost per token, less control), fine-tune/host an open-weight model yourself (more control, more infra burden), or use a pre-built vertical SaaS product (fastest, least flexible)? You'll develop instincts for this tradeoff throughout the curriculum, especially in Track 4 (Product Manager) and Track 5 (Infrastructure Engineer).

## Step-by-step walkthrough

> 💡 **Prefer Jupyter?** Every script below also has a `.ipynb` notebook of the same name in `examples/`, with the explanation broken into markdown cells between runnable code cells, already executed and saved — including the bar chart from step 5 — so you can read the notebooks before installing anything. Open with `jupyter notebook` / `jupyter lab`, or directly in VS Code / Cursor with the Jupyter extension.

1. **Read the concept tables above.** You don't need to memorize every product name — you need to recognize the *categories* (model provider vs. infra vs. vector DB vs. framework) when you encounter a new name later.
2. **Install pandas:**
   ```bash
   cd 01-Foundations-and-Orientation/02-AI-Landscape-and-Industry-Use-Cases/examples
   pip install -r requirements.txt
   ```
3. **Run `01_beginner_use_case_matrix.py`.** It loads `industry_use_cases.csv` — a small hand-built dataset mapping industries to GenAI use cases — with pandas, and shows you how to query it (filter by industry, filter by modality, count use cases per industry). This is the same pattern you'll use throughout this curriculum any time you need to load and filter structured data.
4. **Run `02_intermediate_use_case_recommender.py`.** It's a simple rules-based recommender: give it an industry and a problem description, and it suggests which GenAI capability and modality best fits, using keyword matching against the dataset. This is deliberately simple — real recommendation systems are far more sophisticated — but it teaches the core pattern of "structured data + query logic = decision support tool," which is exactly what you'll build (with an LLM instead of keyword matching) in Track 3.
5. **Run `03_advanced_landscape_chart.py`.** It aggregates the dataset and renders a horizontal bar chart (via `matplotlib`) showing how many documented use cases exist per industry in our dataset, saved as a PNG you can open and inspect. This introduces basic data visualization, a skill you'll lean on constantly when presenting AI findings to stakeholders (especially relevant for Track 4, Product Manager).

### Try it yourself

- Add 3 new rows to `industry_use_cases.csv` for an industry not already covered (e.g. Manufacturing, Government, Real Estate).
- Modify `02_intermediate_use_case_recommender.py` so it also returns the `maturity` field (Emerging vs. Established) in its recommendation, and prefer `Established` use cases when multiple matches are found.
- Re-run `03_advanced_landscape_chart.py` after adding your new rows and confirm the new industry appears in the chart.

## Sub-topic recap

You should now be able to name the major categories of players in the GenAI landscape, distinguish the four content modalities, map a business problem to a plausible GenAI use case, and load/query/visualize structured data with pandas and matplotlib.

---
⬅️ Back to [Track 1 overview](../README.md)
