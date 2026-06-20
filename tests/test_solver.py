from lexilab.feedback import parse_pattern, score_guess
from lexilab.solver import best_guesses, filter_candidates, score_entropy


WORDS = ["cigar", "rebut", "crane", "slate", "trace", "crate"]


def test_filter_candidates_keeps_words_matching_same_feedback() -> None:
    pattern = score_guess("crane", "cigar")

    filtered = filter_candidates(WORDS, "crane", pattern)

    assert filtered == ["cigar"]


def test_filter_candidates_uses_exact_feedback_pattern() -> None:
    filtered = filter_candidates(WORDS, "crane", parse_pattern("GGGGG"))

    assert filtered == ["crane"]


def test_entropy_score_reports_partition_quality() -> None:
    score = score_entropy("crane", WORDS)

    assert score.word == "crane"
    assert score.entropy > 0
    assert score.pattern_count > 1
    assert score.worst_bucket >= 1


def test_best_guesses_returns_highest_entropy_first() -> None:
    scores = best_guesses(WORDS, limit=3)

    assert len(scores) == 3
    assert scores[0].entropy >= scores[1].entropy
