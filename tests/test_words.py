from lexilab.words import load_words


def test_load_packaged_words() -> None:
    words = load_words()

    assert len(words) > 1000
    assert all(len(word) == 5 for word in words)
