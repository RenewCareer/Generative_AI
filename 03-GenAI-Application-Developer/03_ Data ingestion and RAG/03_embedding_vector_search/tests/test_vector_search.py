from pathlib import Path

import numpy as np
import pytest

from genai_kit import HashingEmbedder, load_course_chunks
from genai_kit.testing import load_lesson
from project.faq_search import FaissStore

LESSONS = Path(__file__).resolve().parents[1] / "lessons"
intuition = load_lesson(LESSONS / "01_embedding_intuition.py")
ann = load_lesson(LESSONS / "02_exact_vs_approximate.py")


def make_store() -> FaissStore:
    store = FaissStore(HashingEmbedder())
    store.build(load_course_chunks())
    return store


def test_cosine_similar_words_score_higher():
    toy = intuition.TOY
    assert intuition.cosine(toy["dog"], toy["puppy"]) > intuition.cosine(toy["dog"], toy["car"])


def test_recall_metric():
    found = np.array([[1, 2, 3, 4]])
    truth = np.array([[1, 2, 8, 9]])
    assert ann.recall_at_k(found, truth) == pytest.approx(0.5)


def test_search_finds_expected_document():
    hit = make_store().search("hotel limit per night", k=1)[0]
    assert hit.chunk.doc_id == "expense_policy"


def test_access_filter_is_a_guarantee():
    hits = make_store().search("annual leave days for employees", k=5, access="public")
    assert hits and all(hit.chunk.metadata["access"] == "public" for hit in hits)


def test_filter_finds_rare_matches_beyond_the_overfetch_window():
    store = make_store()
    hits = store.search("refund return window", k=1, access="internal")
    assert hits and hits[0].chunk.metadata["access"] == "internal"


def test_save_and_load_round_trip_in_path_with_spaces(tmp_path):
    store = make_store()
    directory = tmp_path / "folder with spaces"
    store.save(directory)
    restored = FaissStore(HashingEmbedder())
    restored.load(directory)
    assert restored.search("gift cards", k=1)[0].chunk.id == store.search("gift cards", k=1)[0].chunk.id


def test_load_rejects_a_different_embedding_model(tmp_path):
    store = make_store()
    store.save(tmp_path)
    other = HashingEmbedder()
    other.name = "another-model"
    with pytest.raises(ValueError, match="Rebuild"):
        FaissStore(other).load(tmp_path)


def test_search_before_build_fails_clearly():
    with pytest.raises(RuntimeError):
        FaissStore(HashingEmbedder()).search("x")
