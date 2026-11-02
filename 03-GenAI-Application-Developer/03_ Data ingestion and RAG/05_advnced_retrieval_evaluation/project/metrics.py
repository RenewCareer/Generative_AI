"""Retrieval and answer metrics. Implemented by hand so that nothing here is a black box."""

from __future__ import annotations

import math
import re


def hit_at_k(retrieved: list[str], relevant: str, k: int) -> float:
    """Did any relevant item appear in the top k?"""
    return float(relevant in retrieved[:k])


def reciprocal_rank(retrieved: list[str], relevant: str) -> float:
    """1 if the relevant item is first, 1/2 if second, and so on. Rewards early hits."""
    for rank, item in enumerate(retrieved, start=1):
        if item == relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: str, k: int) -> float:
    """Discounted gain, normalised so a perfect ranking scores 1. Duplicates earn no extra."""
    seen: set[str] = set()
    dcg = 0.0
    for rank, item in enumerate(retrieved[:k], start=1):
        if item == relevant and item not in seen:
            dcg += 1 / math.log2(rank + 1)
        seen.add(item)
    return dcg  # The ideal DCG for one relevant item is 1/log2(2) = 1.


def _tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "of", "to", "and", "is", "are", "in", "for", "it", "on", "that", "be", "as"}
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in stop}


def groundedness(answer: str, context: str) -> float:
    """Share of answer sentences mostly supported by the context. A cheap, lexical proxy.

    It catches blatant invention but cannot judge paraphrase or logic. For that, use an
    LLM judge, as in lesson 05.
    """
    answer = re.sub(r"\[\d+\]", "", answer)
    sentences = [sentence for sentence in re.split(r"(?<=[.!?])\s+", answer) if _tokens(sentence)]
    if not sentences:
        return 0.0
    context_tokens = _tokens(context)
    supported = sum(
        len(_tokens(sentence) & context_tokens) / len(_tokens(sentence)) >= 0.6 for sentence in sentences
    )
    return supported / len(sentences)


def contains_all(answer: str, phrases: list[str]) -> float:
    """Exact fact check against the golden dataset."""
    return float(all(phrase.lower() in answer.lower() for phrase in phrases))
