from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from random import Random
from statistics import mean
from typing import Iterable

from lexilab.feedback import Pattern, format_pattern, score_guess, validate_word
from lexilab.solver import GuessScore, best_guesses, filter_candidates, normalize_words, score_entropy


@dataclass(frozen=True)
class SolveStep:
    turn: int
    guess: str
    pattern: str
    entropy: float
    candidates_before: int
    candidates_after: int


@dataclass(frozen=True)
class SolveResult:
    answer: str
    success: bool
    guesses: int
    final_candidates: int
    steps: tuple[SolveStep, ...]


@dataclass(frozen=True)
class BenchmarkSummary:
    sample_size: int
    seed: int
    max_turns: int
    success_rate: float
    average_guesses: float
    worst_success_guesses: int
    failures: int
    guess_distribution: dict[int, int]
    results: tuple[SolveResult, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def sample_words(words: Iterable[str], sample_size: int | None, seed: int) -> list[str]:
    normalized = normalize_words(words)
    if sample_size is None or sample_size >= len(normalized):
        return normalized
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    return sorted(Random(seed).sample(normalized, sample_size))


def _score_known_guess(guess: str, candidates: list[str]) -> GuessScore:
    return score_entropy(guess, candidates)


def solve_answer(
    answer: str,
    answer_words: Iterable[str],
    allowed_guesses: Iterable[str] | None = None,
    max_turns: int = 6,
    first_guess: str | None = None,
) -> SolveResult:
    answer = validate_word(answer)
    candidates = normalize_words(answer_words)
    allowed = normalize_words(allowed_guesses or candidates)

    if answer not in candidates:
        raise ValueError(f"answer {answer!r} must be present in answer_words")
    if max_turns <= 0:
        raise ValueError("max_turns must be positive")

    steps: list[SolveStep] = []

    for turn in range(1, max_turns + 1):
        before = len(candidates)
        if turn == 1 and first_guess is not None:
            guess = validate_word(first_guess)
            guess_score = _score_known_guess(guess, candidates)
        else:
            guess_score = best_guesses(candidates, allowed_guesses=allowed, limit=1)[0]
            guess = guess_score.word

        pattern: Pattern = score_guess(guess, answer)
        next_candidates = filter_candidates(candidates, guess, pattern)

        steps.append(
            SolveStep(
                turn=turn,
                guess=guess,
                pattern=format_pattern(pattern),
                entropy=guess_score.entropy,
                candidates_before=before,
                candidates_after=len(next_candidates),
            )
        )

        if guess == answer:
            return SolveResult(
                answer=answer,
                success=True,
                guesses=turn,
                final_candidates=len(next_candidates),
                steps=tuple(steps),
            )

        candidates = next_candidates
        if not candidates:
            break

    return SolveResult(
        answer=answer,
        success=False,
        guesses=max_turns,
        final_candidates=len(candidates),
        steps=tuple(steps),
    )


def benchmark(
    answer_words: Iterable[str],
    allowed_guesses: Iterable[str] | None = None,
    sample_size: int | None = 250,
    seed: int = 7,
    max_turns: int = 6,
) -> BenchmarkSummary:
    sampled_answers = sample_words(answer_words, sample_size=sample_size, seed=seed)
    allowed = normalize_words(allowed_guesses or sampled_answers)
    first_guess = best_guesses(sampled_answers, allowed_guesses=allowed, limit=1)[0].word

    results = tuple(
        solve_answer(
            answer=answer,
            answer_words=sampled_answers,
            allowed_guesses=allowed,
            max_turns=max_turns,
            first_guess=first_guess,
        )
        for answer in sampled_answers
    )

    successes = [result for result in results if result.success]
    distribution = Counter(result.guesses for result in successes)
    failures = len(results) - len(successes)

    return BenchmarkSummary(
        sample_size=len(sampled_answers),
        seed=seed,
        max_turns=max_turns,
        success_rate=len(successes) / len(results) if results else 0.0,
        average_guesses=mean(result.guesses for result in successes) if successes else 0.0,
        worst_success_guesses=max((result.guesses for result in successes), default=0),
        failures=failures,
        guess_distribution=dict(sorted(distribution.items())),
        results=results,
    )
