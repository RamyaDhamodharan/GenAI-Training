from week3.day14.eval_runner import evaluate_answer


def test_evaluate_answer_passes_when_keywords_exist():
    actual = "Python was created by Guido van Rossum."

    expected_keywords = ["python", "guido", "van rossum"]

    assert evaluate_answer(actual, expected_keywords) is True


def test_evaluate_answer_fails_when_keyword_is_missing():
    actual = "Python is a programming language."

    expected_keywords = ["python", "guido", "van rossum"]

    assert evaluate_answer(actual, expected_keywords) is False