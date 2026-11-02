# Module 01: GenAI Application Foundations

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 2.5 hours | **Next:** [Module 02](../02_LLM%20Applications%20Engineering/README.md)

## Learning outcomes

By the end, students can:

- Explain tokens, context windows and cost, and plan a request around them
- Describe what happens inside an LLM, from tokenizing to sampling
- Read every part of an API request and response
- Structure a small application with configuration, validation and safe error handling

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides 1 to 3: the big picture | `presentation.pptx` |
| 20 min | How the model works | `lessons/04_attention_toy.py`, `lessons/03_temperature_sampling.py` |
| 20 min | Budgets: tokens, context and cost | `lessons/01_tokens_and_context.py` |
| 20 min | Anatomy of a request | `lessons/02_anatomy_of_a_request.py`, `genai-app-foundations/app.py` |
| 25 min | Walk through the example app | `project/study_buddy.py` |
| 40 min | Lab | Below |
| 10 min | Debrief | Below |

## Concepts

**Tokens.** Models read tokens, not words. A common word is often one token, and a rare word may
be several. For English, about 4 characters per token is a useful planning figure. Each model
family tokenizes differently, so use the provider's tokenizer when you need exact counts.

**Context window.** The maximum number of tokens a model can consider in one call, covering the
system prompt, history, retrieved documents, and the reply. It is a budget that everything shares.

**Cost.** Providers charge per token, usually more for output than input. Prices change, so read
them from the provider's page. Lesson 1 uses clearly labelled example prices.

**How generation works.** The model predicts one token at a time. Attention lets each token weigh
the others for context, and that is why "bank" can mean different things in "river bank" and
"bank loan". The model then scores all possible next tokens, and temperature reshapes those scores
before one is sampled.

**Statelessness.** The model remembers nothing between calls. A chat app works by resending the
history each time, so input tokens grow on every turn.

## Run it

From this folder, with the course environment active:

```powershell
python lessons/01_tokens_and_context.py
python lessons/02_anatomy_of_a_request.py
python lessons/03_temperature_sampling.py
python lessons/04_attention_toy.py
python project/study_buddy.py --question "What is a token?"
python project/study_buddy.py --question "What is an embedding?" --stream
python -m pytest tests
```

Your original app is still in [genai-app-foundations/](genai-app-foundations/). It calls the OpenAI
SDK directly, which makes it a good first read, and it needs a key.

### What to expect

From `lessons/03_temperature_sampling.py`:

```
temperature = 0.0
  Paris     100.0% ########################################
temperature = 2.0
  Paris      61.5% ########################
  beautiful  17.6% #######
```

Ask students to predict the temperature 2.0 result before running it.

## Code walkthrough: Study Buddy

| Part of `project/study_buddy.py` | Teaching point |
|---|---|
| `SYSTEM_PROMPT` | Role, format and length are set in one place |
| `validate_question` | Reject bad input before paying for a call |
| `ask` | Always sets `max_tokens` |
| `answer_once` | Different exit codes for bad input and service failure |
| `except Exception` | Log the detail, and show users something safe |

## Industry standards

- **Twelve-factor config:** keys and model names come from the environment
- **Secrets stay out of git:** `.env` is ignored, and only `.env.example` is committed
- **Pinned dependencies:** exact versions in `requirements.txt`
- **Timeouts and retries** on every client
- **Tests that do not need the network**

## Something to discuss

`genai-app-foundations/requirements.txt` lists `pydantic` and `anthropic`, but `app.py` imports
`openai` and `dotenv`. Ask students what would happen on a fresh install. This is why you test
setup instructions in a clean environment.

## Lab

1. Run all four lessons. Change the temperature values and predict the result before running.
2. Add a `--level` flag (beginner or expert) that changes the system prompt.
3. Add a running total of tokens and estimated cost for the session in interactive mode.

**Marking notes.** Task 2: build the prompt in a function, and add a test that each level produces a
different prompt. Task 3: keep totals in a small class rather than globals, and take the prices from
configuration. Students with a key should compare the real answer to the mock one.

## Check for understanding

1. Why does a long chat get slower and more expensive? *The history is resent on each turn.*
2. What happens if the input fills the context window? *The call fails, or there is no room left for the reply, depending on the provider.*
3. Does temperature 0 guarantee identical output? *No. Providers do not promise it, so evaluate rather than assume.*
4. Why is the error message for users different from the one in the logs? *Internal details can leak information, and they do not help users.*
