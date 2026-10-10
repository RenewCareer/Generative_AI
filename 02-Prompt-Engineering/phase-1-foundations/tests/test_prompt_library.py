"""Static tests for the prompt library: run on every change, cost nothing.
The live tests (week2.prompt_library.run_tests) check model behaviour."""
import pytest

from week2.prompt_library import CHECKS, load_library, run_check
from week2.prompt_library.library import PromptTemplate
from week2.prompt_library.run_tests import run_template
from ai_core import Assistant

LIB = load_library()


def test_library_has_at_least_20_templates():
    assert len(LIB) >= 20


@pytest.mark.parametrize("name", sorted(LIB))
def test_template_is_statically_valid(name):
    t = LIB[name]
    assert t.validate() == []
    for test in t.tests:
        t.render(**test.vars)  # must not raise
        for spec in test.checks:
            assert spec["type"] in CHECKS


def test_render_rejects_missing_and_extra_vars():
    t = LIB["summarize_bullets"]
    with pytest.raises(ValueError):
        t.render(text="x")
    with pytest.raises(ValueError):
        t.render(text="x", n_bullets="3", oops="y")


def test_dollar_template_leaves_json_braces_alone():
    t = PromptTemplate(name="t", version="1.0.0", category="c", description="d",
                       variables=["x"], instructions="", template='{"k": "${x}"}')
    assert t.render(x="v") == '{"k": "v"}'


@pytest.mark.parametrize("output,spec,expected", [
    ("- a\n- b\n- c", {"type": "line_count", "value": 3}, True),
    ("Sales.", {"type": "equals", "value": "sales"}, True),
    ("sales and billing", {"type": "one_of", "value": ["sales", "billing"]}, False),
    ('```json\n{"a": 1}\n```', {"type": "json_valid"}, True),
    ('Here: {"a": 1}', {"type": "json_valid"}, False),
    ('{"bugs": []}', {"type": "json_array_len", "key": "bugs", "min": 0, "max": 0}, True),
    ("one two three", {"type": "max_words", "value": 2}, False),
    ("SELECT 1", {"type": "contains_none", "value": ["drop"]}, True),
    ("1. Who?\n2. When?", {"type": "ends_with_question", "min": 2}, True),
])
def test_checks(output, spec, expected):
    assert run_check(output, spec)[0] is expected


def test_runner_marks_failures(make_client):
    t = LIB["classify_ticket"]
    # First test passes, second and third get a wrong label
    client = make_client(["sales", "billing", "billing"])
    result = run_template(Assistant(client=client, remember_history=False), t, 1, False)
    assert (result["passed"], result["total"]) == (2, 3)
    assert client.calls[0]["instructions"] == t.instructions
