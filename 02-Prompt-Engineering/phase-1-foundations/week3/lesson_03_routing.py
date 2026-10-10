"""Lesson 03 — Routing: a cheap classifier sends each request to a specialist prompt.

Run:  python -m week3.lesson_03_routing
      ROUTER_MODEL=gpt-5-nano python -m week3.lesson_03_routing   (bash syntax)

One giant "do everything" system prompt gets long, slow, and contradictory.
Instead:  router (small, fast)  ->  specialist (focused instructions)  ->  answer
With a fallback when the router is unsure. This is the seed of an agent (Week 11).
"""
import os

from ai_core import Assistant, AssistantError

SPECIALISTS = {
    "python_tutor": "You are a Python tutor for beginners. Explain with a tiny runnable "
                    "code example. Max 120 words.",
    "career_coach": "You are a tech career coach. Give practical, specific next steps as a "
                    "numbered list of at most 4 items.",
    "math_helper": "You are a maths helper. Solve step by step, numbering each step, and "
                   "box the final answer like [[answer]].",
    "general": "You are a helpful assistant. If the request is outside your knowledge, "
               "say so. Max 100 words.",
}
CONFIDENCE_THRESHOLD = 0.6

ROUTER_INSTRUCTIONS = (
    "Route the user's message to the best specialist.\n"
    + "\n".join(f"- {name}: {text.split('.')[0]}" for name, text in SPECIALISTS.items())
    + '\nReturn JSON only: {"route": <name>, "confidence": <0..1>, "reason": <short>}'
)

router = Assistant(model=os.getenv("ROUTER_MODEL"), instructions=ROUTER_INSTRUCTIONS,
                   remember_history=False)
worker = Assistant(remember_history=False)


def handle(message: str) -> None:
    try:
        decision, _ = router.complete_json(f"<message>{message}</message>")
        route, conf = decision.get("route"), float(decision.get("confidence", 0))
    except (AssistantError, ValueError, TypeError) as e:  # router broke -> don't crash
        route, conf, decision = "general", 0.0, {"reason": f"router error: {e}"}

    # Validate the router's output — it's model output, not a guaranteed enum.
    if route not in SPECIALISTS or conf < CONFIDENCE_THRESHOLD:
        fallback_reason = "unknown route" if route not in SPECIALISTS else f"low confidence {conf:.2f}"
        print(f"   (fallback to general: {fallback_reason})")
        route = "general"

    reply = worker.complete(message, instructions=SPECIALISTS[route])
    print(f"\n>>> {message}\n[{route} | conf {conf:.2f} | {decision.get('reason', '')}]\n{reply.text}")


for msg in [
    "How do I reverse a list in Python?",
    "I'm a teacher, how do I move into a data analyst job?",
    "What is 15% of 240, then add 18?",
    "What's the capital of Australia?",
    "Write a python script that calculates my maths homework",  # ambiguous on purpose
]:
    handle(msg)

print(f"\nrouter: {router.usage}\nworker: {worker.usage}")
print("""
Discuss:
- The router call should be much cheaper than the worker call. Is it?
- Look at the ambiguous last message. Where did it go? Is that what you'd want?
- Every route needs its own tests (Week 2 library style). The router does too:
  a labelled set of messages -> expected routes, scored like lesson 03 of Week 2.
""")
