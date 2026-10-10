# Phase 1 — Prompt engineering foundations (Weeks 1–3)

Direct model interaction and prompt design, with the OpenAI **Responses API** in Python.

| Week | Topic | Practical | Start here |
|---|---|---|---|
| 1 | OpenAI API & Python | Reusable AI assistant | [week1/README.md](week1/README.md) |
| 2 | Prompt design & instruction hierarchy | Prompt library, 20 tested templates | [week2/README.md](week2/README.md) |
| 3 | Advanced prompting strategies | Consistent beginner-lesson generator | [week3/README.md](week3/README.md) |

## Setup (once)

```bash
cd 02-Prompt-Engineering/phase-1-foundations
pip install -r requirements.txt
cp .env.example .env        # PowerShell: Copy-Item .env.example .env   — then paste your key
python -m pytest -q         # 59 offline tests, no key needed, should all pass
python -m week1.lesson_01_hello
```

**Always run from `phase-1-foundations/`** using `python -m weekN.module_name` — that's what lets every week import the shared `ai_core` package.

## How the code is organised

```
phase-1-foundations/
├── ai_core/                 ← built in Week 1, reused by Weeks 2 & 3
│   ├── assistant.py           Assistant: calls, history, errors, usage, cost, JSON helper
│   ├── config.py              settings from env vars / .env
│   ├── pricing.py             cost estimates (verify prices!)
│   └── jsonutil.py            tolerant JSON extraction
├── week1/  lessons 01-04 + chat.py (practical)
├── week2/  lessons 01-04 + prompt_library/ (practical: 20 .toml templates + checks + runner)
├── week3/  lessons 01-04 + lesson_generator/ (practical) + readability.py
└── tests/  fake OpenAI client + 59 tests
```

## How to study each week (senior-engineer method)

1. **Read the week README** for the day's concepts.
2. **Predict, then run** each lesson. Write your prediction down first. The gap between prediction and result is where you learn.
3. **Read the code** — the docstrings and comments are part of the lesson.
4. **Do the exercises.** Not optional. Each one is something you'll do on the job.
5. **Answer the self-check** questions without notes. If you can't, re-run the lesson.
6. **Keep `pytest` green** whenever you change shared code.

## Cost

Everything in Phase 1 on a mini-class model costs well under **$1** total. Set a budget limit on your OpenAI project anyway — it's a good habit. Every script prints its token usage and estimated cost.

## Default model

`gpt-5-mini` (override with `OPENAI_MODEL` in `.env` or `--model`). It's a *reasoning* model: it doesn't accept `temperature`, and it spends hidden reasoning tokens. If you switch to a non-reasoning model like `gpt-4.1-mini`, you can pass `temperature`. Model names and availability change — check the [models page](https://platform.openai.com/docs/models).
