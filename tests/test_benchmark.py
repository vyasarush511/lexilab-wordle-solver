from lexilab.benchmark import benchmark, solve_answer


WORDS = ["cigar", "rebut", "crane", "slate", "trace", "crate", "later", "arise"]


def test_solve_answer_returns_steps_until_success() -> None:
    result = solve_answer("cigar", WORDS, max_turns=6)

    assert result.success
    assert result.answer == "cigar"
    assert result.guesses >= 1
    assert result.steps[-1].guess == "cigar"


def test_benchmark_reports_distribution() -> None:
    summary = benchmark(WORDS, sample_size=5, seed=1, max_turns=6)

    assert summary.sample_size == 5
    assert summary.success_rate > 0
    assert summary.guess_distribution
    assert len(summary.results) == 5
