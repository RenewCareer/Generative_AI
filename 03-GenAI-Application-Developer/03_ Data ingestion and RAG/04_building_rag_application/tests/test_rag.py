import pytest

from genai_kit import Chunk, MockClient, VectorIndex, load_course_chunks
from project.policy_assistant import render
from project.rag import REFUSAL, RagPipeline, extract_citations


class CountingMock(MockClient):
    def __init__(self):
        super().__init__()
        self.calls = 0
        self.last_prompt = ""

    def complete(self, messages, **kwargs):
        self.calls += 1
        self.last_prompt = messages[-1]["content"]
        return super().complete(messages, **kwargs)


@pytest.fixture(scope="module")
def index():
    return VectorIndex().add(load_course_chunks())


def test_answer_is_grounded_and_cited(index):
    result = RagPipeline(index, MockClient()).ask("What is the hotel limit per night?")
    assert "180 dollars" in result.answer
    assert result.cited and not result.refused
    assert result.sources[result.cited[0] - 1].chunk.doc_id == "expense_policy"


def test_prompt_contains_sources_and_question(index):
    llm = CountingMock()
    RagPipeline(index, llm).ask("How long does express delivery take?")
    assert "[1] (source:" in llm.last_prompt
    assert "Question: How long does express delivery take?" in llm.last_prompt


def test_unanswerable_question_is_refused(index):
    result = RagPipeline(index, MockClient()).ask("Who won the football world cup in 2018?")
    assert result.refused and REFUSAL in result.answer


def test_no_relevant_hits_skips_the_model():
    llm = CountingMock()
    empty = VectorIndex().add([Chunk("a#0", "a", "zebra zebra zebra")])
    result = RagPipeline(empty, llm, min_score=0.9).ask("hotel limit")
    assert result.refused and llm.calls == 0


def test_invented_citations_are_flagged(index):
    llm = MockClient(lambda messages, system, tools: "Up to 180 dollars [1] and also [9].")
    result = RagPipeline(index, llm).ask("What is the hotel limit per night?")
    assert result.cited == [1] and result.invalid_citations == [9]
    assert "do not exist" in render(result)


def test_empty_question_rejected(index):
    with pytest.raises(ValueError):
        RagPipeline(index, MockClient()).ask("   ")


def test_extract_citations():
    assert extract_citations("a [2] b [1] c [2]") == [1, 2]
