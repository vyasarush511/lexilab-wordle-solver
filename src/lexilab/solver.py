from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log2
from typing import Iterable, Sequence

from lexilab.feedback import Pattern, score_guess, validate_word


@dataclass(frozen=True)
class GuessScore:
    word: str
    entropy: float
    expected_remaining: float
    worst_bucket: int
    pattern_count: int


def normalize_words(words: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    normalized_words: list[str] = []

    for word in words:
        normalized = validate_word(word)
        if normalized in seen:
            continue
        seen.add(normalized)
        normalized_words.append(normalized)

    return normalized_words


def filter_candidates(candidates: Iterable[str], guess: str, pattern: Pattern) -> list[str]:
    guess = validate_word(guess)
    return [
        candidate
        for candidate in normalize_words(candidates)
        if score_guess(guess, candidate) == pattern
    ]


def score_entropy(guess: str, candidates: Sequence[str]) -> GuessScore:
    guess = validate_word(guess)
    if not candidates:
        raise ValueError("cannot score a guess with no candidate answers")

    buckets = Counter(score_guess(guess, answer) for answer in candidates)
    total = len(candidates)

    entropy = 0.0
    expected_remaining = 0.0
    for bucket_size in buckets.values():
        probability = bucket_size / total
        entropy += probability * log2(1 / probability)
        expected_remaining += probability * bucket_size

    return GuessScore(
        word=guess,
        entropy=entropy,
        expected_remaining=expected_remaining,
        worst_bucket=max(buckets.values()),
        pattern_count=len(buckets),
    )


def partition_counts(guess: str, candidates: Sequence[str]) -> Counter[Pattern]:
    """Group candidate answers by the feedback pattern a guess would produce."""

    guess = validate_word(guess)
    return Counter(score_guess(guess, answer) for answer in candidates)


def best_guesses(
    candidates: Iterable[str],
    allowed_guesses: Iterable[str] | None = None,
    limit: int = 10,
) -> list[GuessScore]:
    candidate_words = normalize_words(candidates)
    candidate_set = set(candidate_words)
    guess_words = normalize_words(allowed_guesses or candidate_words)

    scores = [score_entropy(guess, candidate_words) for guess in guess_words]
    scores.sort(
        key=lambda score: (
            -score.entropy,
            score.expected_remaining,
            score.worst_bucket,
            score.word not in candidate_set,
            score.word,
        )
    )
    return scores[:limit]
