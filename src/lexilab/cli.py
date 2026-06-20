from __future__ import annotations

import argparse

from lexilab.benchmark import benchmark, solve_answer
from lexilab.feedback import format_pattern, parse_pattern, validate_word
from lexilab.report import write_html_report, write_json_report
from lexilab.solver import best_guesses, filter_candidates
from lexilab.words import load_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explainable Wordle solver")
    parser.add_argument(
        "--words",
        help="Path to a newline-separated 5-letter word list. Defaults to bundled corpus.",
    )

    subparsers = parser.add_subparsers(dest="command")

    rank = subparsers.add_parser("rank", help="Show the best guesses for a word list")
    rank.add_argument("--top", type=int, default=10, help="Number of guesses to show")
    rank.add_argument("--sample-size", type=int, default=750)
    rank.add_argument("--seed", type=int, default=7)

    solve = subparsers.add_parser("solve", help="Simulate solving a known answer")
    solve.add_argument("answer", help="Hidden answer to simulate")
    solve.add_argument("--max-turns", type=int, default=6)
    solve.add_argument("--sample-size", type=int, default=750)
    solve.add_argument("--seed", type=int, default=7)

    suggest = subparsers.add_parser("suggest", help="Suggest a guess from known clues")
    suggest.add_argument(
        "--clue",
        action="append",
        default=[],
        metavar="GUESS:PATTERN",
        help="Known clue, for example crane:GYY.. . Can be repeated.",
    )
    suggest.add_argument("--top", type=int, default=10, help="Number of guesses to show")
    suggest.add_argument("--sample-size", type=int, default=None)
    suggest.add_argument("--seed", type=int, default=7)

    bench = subparsers.add_parser("benchmark", help="Benchmark the solver")
    bench.add_argument("--sample-size", type=int, default=250)
    bench.add_argument("--seed", type=int, default=7)
    bench.add_argument("--max-turns", type=int, default=6)
    bench.add_argument("--json", default="reports/benchmark.json")
    bench.add_argument("--html", default="docs/index.html")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    words = load_words(args.words)

    command = args.command or "rank"
    if command == "rank":
        _rank(words, top=args.top, sample_size=args.sample_size, seed=args.seed)
    elif command == "solve":
        _solve(
            words,
            answer=args.answer,
            max_turns=args.max_turns,
            sample_size=args.sample_size,
            seed=args.seed,
        )
    elif command == "suggest":
        _suggest(
            words,
            clues=args.clue,
            top=args.top,
            sample_size=args.sample_size,
            seed=args.seed,
        )
    elif command == "benchmark":
        _benchmark(words, args.sample_size, args.seed, args.max_turns, args.json, args.html)
    else:
        raise SystemExit(f"Unknown command: {command}")


def _rank(words: list[str], top: int, sample_size: int, seed: int) -> None:
    candidates = _deterministic_sample(words, sample_size=sample_size, seed=seed)
    print(f"Loaded {len(words)} words; ranking over {len(candidates)} sampled candidates.")
    print("Top opening guesses:")
    for score in best_guesses(candidates, limit=top):
        print(
            f"{score.word:>5}  entropy={score.entropy:.3f}  "
            f"expected_left={score.expected_remaining:.2f}  "
            f"worst_bucket={score.worst_bucket}"
        )


def _solve(words: list[str], answer: str, max_turns: int, sample_size: int, seed: int) -> None:
    candidates = _deterministic_sample(
        words,
        sample_size=sample_size,
        seed=seed,
        include=[answer],
    )
    result = solve_answer(answer=answer, answer_words=candidates, max_turns=max_turns)
    print(f"Simulating answer: {answer}")
    for step in result.steps:
        print(
            f"{step.turn}. {step.guess} -> {step.pattern}  "
            f"entropy={step.entropy:.3f}  "
            f"{step.candidates_after}/{step.candidates_before} candidates remain"
        )
    if result.success:
        print(f"Solved in {result.guesses} guesses.")
    else:
        print(f"Missed after {max_turns} guesses with {result.final_candidates} candidates left.")


def _suggest(
    words: list[str],
    clues: list[str],
    top: int,
    sample_size: int | None,
    seed: int,
) -> None:
    candidates = (
        _deterministic_sample(words, sample_size=sample_size, seed=seed)
        if sample_size is not None
        else words
    )
    print(f"Loaded {len(candidates)} candidate words.")

    for clue in clues:
        try:
            guess, raw_pattern = clue.split(":", 1)
        except ValueError as exc:
            raise SystemExit(f"Invalid clue {clue!r}. Use GUESS:PATTERN, like crane:GYY..") from exc
        pattern = parse_pattern(raw_pattern)
        candidates = filter_candidates(candidates, guess, pattern)
        print(f"{guess.lower()} -> {format_pattern(pattern)} leaves {len(candidates)} candidates")

    if not candidates:
        print("No candidates remain. Check the clue pattern or word list.")
        return

    print("Best next guesses:")
    for score in best_guesses(candidates, limit=top):
        print(
            f"{score.word:>5}  entropy={score.entropy:.3f}  "
            f"expected_left={score.expected_remaining:.2f}  "
            f"worst_bucket={score.worst_bucket}"
        )


def _benchmark(
    words: list[str],
    sample_size: int,
    seed: int,
    max_turns: int,
    json_path: str,
    html_path: str,
) -> None:
    summary = benchmark(
        words,
        sample_size=sample_size,
        seed=seed,
        max_turns=max_turns,
    )
    json_report = write_json_report(summary, json_path)
    html_report = write_html_report(summary, html_path)

    print(f"Benchmarked {summary.sample_size} answers with seed {summary.seed}.")
    print(f"Success rate: {summary.success_rate:.1%}")
    print(f"Average guesses: {summary.average_guesses:.2f}")
    print(f"Worst successful solve: {summary.worst_success_guesses}")
    print(f"Failures: {summary.failures}")
    print(f"JSON report: {json_report}")
    print(f"HTML report: {html_report}")


def _deterministic_sample(
    words: list[str],
    sample_size: int | None,
    seed: int,
    include: list[str] | None = None,
) -> list[str]:
    if sample_size is None or sample_size >= len(words):
        sampled = list(words)
    else:
        from random import Random

        if sample_size <= 0:
            raise SystemExit("sample-size must be positive")
        sampled = sorted(Random(seed).sample(words, sample_size))

    seen = set(sampled)
    for word in include or []:
        normalized = validate_word(word)
        if normalized not in seen:
            sampled.append(normalized)
            seen.add(normalized)
    return sampled
