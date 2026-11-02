"""Small text analysis helpers shared by the offline embedder, BM25 and the mock."""

from __future__ import annotations

import re

STOPWORDS = frozenset(
    "a about all an and any are as at be been but by can could did do does for from get got had has "
    "have how i if in into is it its me my no not of on or our she should so than that the their them "
    "then there these they this to up us was we were what when where which who why will with would "
    "you your".split()
)


def stem(word: str) -> str:
    """A very light stemmer: plural 'items' becomes 'item', and 'class' stays as it is."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def analyze(text: str, pattern: str = r"[a-z0-9]+") -> list[str]:
    """Lowercase, split, drop stopwords and stem. Search engines call this an analyzer."""
    return [stem(word) for word in re.findall(pattern, text.lower()) if word not in STOPWORDS]
