import pytest

from lexilab.feedback import Feedback, format_pattern, parse_pattern, score_guess


def test_all_green_when_guess_matches_answer() -> None:
    assert format_pattern(score_guess("cigar", "cigar")) == "GGGGG"


def test_yellow_and_gray_feedback() -> None:
    assert format_pattern(score_guess("crane", "cigar")) == "GYY.."


def test_repeated_guess_letters_are_consumed() -> None:
    assert format_pattern(score_guess("eerie", "rebel")) == "YGY.."


def test_repeated_answer_letters_are_consumed_after_green_matches() -> None:
    assert format_pattern(score_guess("allee", "eagle")) == "YY.YG"


def test_parse_pattern_accepts_common_gray_symbols() -> None:
    assert parse_pattern("GY._-") == (
        Feedback.GREEN,
        Feedback.YELLOW,
        Feedback.GRAY,
        Feedback.GRAY,
        Feedback.GRAY,
    )


def test_invalid_words_raise_clear_error() -> None:
    with pytest.raises(ValueError):
        score_guess("word", "cigar")
