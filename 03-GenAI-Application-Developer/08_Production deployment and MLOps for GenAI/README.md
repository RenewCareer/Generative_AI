# Module 08: Production Deployment and MLOps for GenAI

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3.5 hours, plus the capstone

## Learning outcomes

By the end, students can:

- Package a service into a small, secure container
- Monitor latency, tokens, cost and quality
- Release prompts safely, with canaries, gates and instant rollback
- Enforce a hard spending limit, and load test a real server

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides: what can change | `presentation.pptx` |
| 30 min | Container walkthrough, and run it | `Dockerfile`, `docker-compose.yml` |
| 25 min | Logs and metrics | `lessons/01_logs_and_metrics.py` |
| 30 min | Prompt canary | `lessons/02_prompt_canary.py`, `project/release.py` |
| 15 min | Budget guard | `lessons/03_budget_guard.py` |
| 20 min | Load test | `lessons/04_load_test.py` |
| 20 min | CI pipeline | `ci/github-actions.yml` |
| Open | Capstone | Below |

## Concepts

**More than code can change behaviour.** Prompts, models, data and traffic all change your product. If code is unchanged and answers got
worse, any of those could be the cause. That is why output quality needs monitoring as much as servers do.

**The container.**

| Practice | Why |
|---|---|
| Multi-stage build | Build tools stay out of the final image |
| Non-root user | Limits the damage if the app is compromised |
| No secrets in the image | Anyone who can pull an image can read them |
| Health check | The platform can see if the service is working |
| Pinned dependencies | Repeatable builds |

**One worker per container.** Metrics and the budget counter live in process memory, so several workers would report inconsistent numbers.
Scale by running more containers, and use a shared store such as Redis for the budget.

**Liveness and readiness.**

| Endpoint | If it fails | Meaning |
|---|---|---|
| `/healthz` | Restart the container | The process is broken |
| `/readyz` | Send no traffic, and do not restart | Still starting, or a dependency is missing |

Confusing them can turn a slow startup into a restart loop.

**What to monitor.** Traffic, errors, latency percentiles, tokens, cost and quality. Averages hide slow calls, so read p95. Log IDs and sizes by
default, because prompts may contain personal data. Alert on what users feel, such as error rate and spend rate.

**Prompt canary.** Send a new prompt to a small share of users, assigned by a hash of the user ID, so that each person stays on one version.
Decide promotion rules before you see the results.

| Decision | When |
|---|---|
| Wait | Too few requests to judge |
| Promote | Errors, p95 latency and quality are all within limits |
| Roll back | Any one signal is out of limits. This is a config change, and needs no deployment |

**Budget guard.** A hard daily limit returns a 503. A stopped service is annoying, and a runaway bill can be far worse. Alert at 50% and 80%.

## Run it

Lessons and tests need no Docker:

```powershell
python lessons/01_logs_and_metrics.py
python lessons/02_prompt_canary.py
python lessons/03_budget_guard.py
python lessons/04_load_test.py
python -m pytest tests
python -m uvicorn project.main:app --port 8080
```

### Run in Docker

Start Docker Desktop first. Then, from this folder:

```powershell
docker compose up --build
```

- API docs: http://localhost:8080/docs (API key `dev-key-123`)
- Metrics: http://localhost:8080/metrics
- Prometheus: http://localhost:9090. Try the query `genai_requests_total`

Compose reads `../.env` if it exists, and otherwise runs in mock mode. The image can also be built directly, from the track root:

```powershell
docker build -f "08_Production deployment and MLOps for GenAI/Dockerfile" -t genai-service:1.0.0 .
```

> **Not yet verified.** Docker Desktop was not running when this was written, so the image build and the compose
> stack have not been run. `docker-compose.yml` passed syntax validation, and the service code is tested. Run the
> build once before you teach this, and keep time for fixes. The Prometheus image tag is a pinned version to check.

### What to expect

From the load test, with a mock model that sleeps 50 ms. Numbers vary by machine and by run:

```
 concurrent    req/s    p50 ms    p95 ms  errors
          1     16.0        63        65       0
          5     69.9        69        80       0
         20    194.9        77       109       0
```

This shows the service's own overhead. It says nothing about a real model's speed, and provider rate limits usually hit you first.

From the canary lesson:

```
Config: 10% canary. Over 10,000 users: {'1.0.0': 9002, '1.1.0': 998}
  Too little data yet   WAIT      only 50 of 200 requests so far
  Healthy canary        PROMOTE   all signals are within limits
  Answers got worse     ROLLBACK  quality 0.82 against 0.91
  Latency regression    ROLLBACK  p95 latency 2600 ms against 1800 ms
```

## Code walkthrough

| Part | Teaching point |
|---|---|
| `main.create_app` | Loading happens in `lifespan`, and readiness stays false until it finishes |
| `observability.JsonFormatter` | One searchable JSON object per line |
| `observability.Metrics` | Traffic, latency, tokens, cost and budget |
| `release.PromptRegistry` | Prompts are files, and config picks the live one |
| `release.BudgetGuard` | Resets daily, with a lock for thread safety |
| `release.promotion_decision` | Rollback wins over waiting, whatever the sample size |
| `ci/github-actions.yml` | Tests, then the eval gate, then build and scan. Copy it to `.github/workflows/` to activate it |

## Industry standards

- Immutable images: build once, and promote the same image
- A secret manager, such as Vault or a cloud equivalent
- Pinned model versions where offered, with a plan for retirement
- Image scanning in CI
- OpenTelemetry for vendor-neutral traces
- Managed containers (Cloud Run, ECS, Azure Container Apps) as a sensible first target. Use Kubernetes if you already run it

## Capstone

1. Run the service in Docker, send traffic with the load test, and find your metrics in Prometheus.
2. Add prompt `v1.2.0`, send it to 10% of users, and use `promotion_decision` to justify promote or roll back.
3. Copy the CI template to your repository, and show a failing evaluation blocking a merge.

**Each student or team presents:** the architecture, an evaluation report, one security finding they fixed, and an estimated cost per
thousand requests. Mark them on whether their decisions are backed by evidence.

## Check for understanding

1. Answers got worse, and the code has not changed. What could be the cause? *A prompt, a model update, new data, or new kinds of questions.*
2. Why not put keys in the image? *Anyone who can pull the image can read them.*
3. What is the difference between liveness and readiness? *One triggers a restart, the other only stops traffic.*
4. Why assign canaries by a hash of the user ID? *So that each person gets a consistent experience, and the signals stay clean.*
