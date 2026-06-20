from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Iterable


WORD_LENGTH = 5


class Feedback(str, Enum):
    """One square of Wordle feedback."""

    GREEN = "G"
    YELLOW = "Y"
    GRAY = "."


Pattern = tuple[Feedback, Feedback, Feedback, Feedback, Feedback]


def validate_word(word: str) -> str:
    normalized = word.strip().lower()
    if len(normalized) != WORD_LENGTH or not normalized.isalpha():
        raise ValueError(f"expected a {WORD_LENGTH}-letter alphabetic word: {word!r}")
    return normalized


def score_guess(guess: str, answer: str) -> Pattern:
    """Return Wordle feedback for a guess against an answer.

    Green matches are consumed first. Yellow matches can only use the remaining
    unmatched letters, which is the key rule for repeated letters.
    """

    guess = validate_word(guess)
    answer = validate_word(answer)

    pattern: list[Feedback | None] = [None] * WORD_LENGTH
    remaining_answer_letters: Counter[str] = Counter()

    for index, (guess_letter, answer_letter) in enumerate(zip(guess, answer)):
        if guess_letter == answer_letter:
            pattern[index] = Feedback.GREEN
        else:
            remaining_answer_letters[answer_letter] += 1

    for index, guess_letter in enumerate(guess):
        if pattern[index] is not None:
            continue
        if remaining_answer_letters[guess_letter] > 0:
            pattern[index] = Feedback.YELLOW
            remaining_answer_letters[guess_letter] -= 1
        else:
            pattern[index] = Feedback.GRAY

    return tuple(pattern)  # type: ignore[return-value]


def parse_pattern(raw_pattern: str | Iterable[str | Feedback]) -> Pattern:
    if isinstance(raw_pattern, str):
        tokens = tuple(raw_pattern.strip().upper())
    else:
        tokens = tuple(raw_pattern)

    if len(tokens) != WORD_LENGTH:
        raise ValueError(f"expected {WORD_LENGTH} feedback tokens")

    mapping = {
        "G": Feedback.GREEN,
        "Y": Feedback.YELLOW,
        ".": Feedback.GRAY,
        "_": Feedback.GRAY,
        "-": Feedback.GRAY,
        Feedback.GREEN: Feedback.GREEN,
        Feedback.YELLOW: Feedback.YELLOW,
        Feedback.GRAY: Feedback.GRAY,
    }

    try:
        return tuple(mapping[token] for token in tokens)  # type: ignore[return-value]
    except KeyError as exc:
        raise ValueError(f"unknown feedback token: {exc.args[0]!r}") from exc


def format_pattern(pattern: Pattern) -> str:
    return "".join(square.value for square in pattern)
