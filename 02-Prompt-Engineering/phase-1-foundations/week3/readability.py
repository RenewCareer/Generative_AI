"""Cheap, deterministic text metrics for "is this beginner-friendly?".

Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
  90-100 very easy | 60-70 plain English | 30-50 college | <30 academic
The syllable counter is a heuristic — good enough to compare texts, not to grade them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


def strip_markdown(md: str) -> str:
    text = re.sub(r"```.*?```", " ", md, flags=re.DOTALL)  # code blocks
    text = re.sub(r"`[^`]*`", "code", text)                 # inline code -> one word
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>|]", "", text)
    return text


def count_syllables(word: str) -> int:
    w = word.lower()
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(n, 1)


@dataclass
class Readability:
    words: int
    sentences: int
    avg_sentence_len: float
    flesch: float


def analyze(md: str) -> Readability:
    text = strip_markdown(md)
    # Sentence ends: . ! ? or a line break (headings/list items count as sentences).
    sentences = [s for s in re.split(r"[.!?]+|\n+", text) if re.search(r"[A-Za-z]", s)]
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
    n_w, n_s = len(words), max(len(sentences), 1)
    if n_w == 0:
        return Readability(0, 0, 0.0, 0.0)
    syl = sum(count_syllables(w) for w in words)
    flesch = 206.835 - 1.015 * (n_w / n_s) - 84.6 * (syl / n_w)
    return Readability(n_w, n_s, round(n_w / n_s, 1), round(flesch, 1))
