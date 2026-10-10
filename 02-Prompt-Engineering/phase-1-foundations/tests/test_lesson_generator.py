import json

import pytest

from ai_core import Assistant, AssistantError
from week3.lesson_generator.pipeline import generate_lesson
from week3.lesson_generator.verify import split_sections, verify_lesson, verify_plan
from week3.readability import analyze, count_syllables

PLAN = {
    "title": "APIs: How Apps Talk to Each Other",
    "objectives": ["Explain what an API is", "Describe a request and a response",
                   "Spot APIs in apps you use"],
    "key_terms": [{"term": "API", "plain_definition": "a way for programs to ask each other for things"},
                  {"term": "request", "plain_definition": "a message asking for something"}],
    "analogy": "A waiter in a restaurant", "example": "A weather app", "exercise": "List 3 apps",
    "misconception": "An API is not a database",
}

GOOD_LESSON = """# APIs: How Apps Talk to Each Other

## What you'll learn
- Explain what an API is.
- Describe a request and a response.
- Spot APIs in apps you use every day.

## Why it matters
You use apps all day. Most of them get their data from somewhere else. APIs make that possible. When you know what an API is, a lot of tech news starts to make sense.

## Key ideas
An **API** is a way for one program to ask another program for something. Think of a waiter in a restaurant. You do not walk into the kitchen. You tell the waiter what you want. The waiter brings the order to the kitchen. Then the waiter brings your food back to you.

The message you send is called a **request**. A request is a message that asks for something. The answer that comes back is called a response. The kitchen is the other program. You never see how it works inside. You only see the menu and the food.

Many people think an API is a database. It is not. A database stores data. An API is the door you knock on to ask for it. Some APIs use a database behind the door. Some do not use one at all.

## Example
Open a weather app on your phone. The app does not measure the weather itself. It sends a request to a weather service. The request says which town you are in. The service looks up the weather for that town. It sends back a response with the temperature and the chance of rain. Your app then shows that data with nice icons. All of this takes less than a second. You never see the request or the response. You just see the result on your screen.

## Try it yourself
1. Pick three apps on your phone.
2. For each app, write down one piece of data it shows you.
3. Guess where that data comes from.
4. Ask yourself: did the app make it, or did it ask another service?

## Quick check
1. What is an API in your own words?
2. What is the name for the message an app sends to ask for data?
3. Is an API the same thing as a database?

## Summary
- An API lets one program ask another program for things.
- A request goes out and a response comes back.
- Apps use APIs all the time to get data they do not have.
"""


def test_good_lesson_passes_verification():
    assert verify_lesson(GOOD_LESSON, PLAN) == []


def test_sections_parsed_in_order():
    assert list(split_sections(GOOD_LESSON))[0] == "What you'll learn"
    assert list(split_sections(GOOD_LESSON))[-1] == "Summary"


def test_missing_section_and_bad_quiz_are_reported():
    broken = GOOD_LESSON.replace("## Example", "## Worked example").replace(
        "3. Is an API the same thing as a database?", "")
    issues = verify_lesson(broken, PLAN)
    assert any("Example" in i for i in issues)
    assert any("Quick check" in i for i in issues)


def test_unexplained_key_term_is_reported():
    plan = {**PLAN, "key_terms": [{"term": "endpoint", "plain_definition": "x"}]}
    assert any("endpoint" in i for i in verify_lesson(GOOD_LESSON, plan))


def test_plan_validation():
    assert verify_plan(PLAN) == []
    assert verify_plan({**PLAN, "objectives": ["one"]})
    assert verify_plan([1, 2])


def test_readability_basics():
    assert count_syllables("cat") == 1
    assert count_syllables("table") == 2
    assert analyze(GOOD_LESSON).flesch > 60


CRITIC_PASS = json.dumps({"scores": {"accuracy": 5, "beginner_fit": 5, "clarity": 4, "engagement": 4},
                          "issues": []})
CRITIC_FAIL = json.dumps({"scores": {"accuracy": 5, "beginner_fit": 3, "clarity": 4, "engagement": 4},
                          "issues": ["'request' needs a simpler example"]})


def test_pipeline_happy_path(make_client):
    client = make_client([json.dumps(PLAN), GOOD_LESSON, CRITIC_PASS])
    result = generate_lesson("What is an API?", bot=Assistant(client=client), log=lambda _: None)
    assert result.passed
    assert len(result.rounds) == 1
    assert len(client.calls) == 3  # plan, write, critique


def test_pipeline_skips_critic_when_structure_broken_then_revises(make_client):
    broken = GOOD_LESSON.replace("## Summary", "## Wrap-up")
    client = make_client([json.dumps(PLAN), broken, GOOD_LESSON, CRITIC_PASS])
    result = generate_lesson("What is an API?", bot=Assistant(client=client), log=lambda _: None)
    assert result.passed
    assert len(result.rounds) == 2
    # round 0 failed verification -> no critic call; revise received the issue text
    assert "Wrap-up" in client.calls[2]["input"] and "Summary" in client.calls[2]["input"]


def test_pipeline_stops_after_max_revisions(make_client):
    client = make_client([json.dumps(PLAN), GOOD_LESSON, CRITIC_FAIL, GOOD_LESSON, CRITIC_FAIL])
    result = generate_lesson("x", bot=Assistant(client=client), max_revisions=1, log=lambda _: None)
    assert not result.passed
    assert len(result.rounds) == 2


def test_invalid_plan_is_retried_then_rejected(make_client):
    bad = json.dumps({**PLAN, "objectives": ["only one"]})
    client = make_client([bad, bad])
    with pytest.raises(AssistantError, match="invalid plan"):
        generate_lesson("x", bot=Assistant(client=client), log=lambda _: None)


def test_complete_json_self_corrects(make_client):
    client = make_client(["sorry, here it is: not json", '{"ok": true}'])
    data, _ = Assistant(client=client).complete_json("give json")
    assert data == {"ok": True}
    assert client.calls[1]["input"][-1]["content"].startswith("That was not valid JSON")
