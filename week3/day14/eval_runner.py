import json
from pathlib import Path

from week3.day14.prompt import build_prompt
from week3.day14.model import model_call


GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


def load_golden_set():
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def evaluate_answer(actual: str, expected_keywords: list[str]) -> bool:
    actual_normalized = normalize(actual)

    return all(
        keyword.lower() in actual_normalized
        for keyword in expected_keywords
    )


def run_evaluation(model_call):
    cases = load_golden_set()

    passed = 0
    total = len(cases)

    for case in cases:
        prompt = build_prompt(
            context=case["context"],
            question=case["question"],
        )

        actual = model_call(prompt)

        if evaluate_answer(actual, case["expected_keywords"]):
            passed += 1
        else:
            print(f"\n❌ Case {case['id']} failed")
            print(f"Question: {case['question']}")
            print(f"Expected keywords: {case['expected_keywords']}")
            print(f"Actual answer: {actual}")

    pass_rate = (passed / total) * 100

    print("\n--------------------")
    print(f"Passed: {passed}/{total}")
    print(f"Pass rate: {pass_rate:.2f}%")

    return pass_rate


if __name__ == "__main__":
    run_evaluation(model_call)