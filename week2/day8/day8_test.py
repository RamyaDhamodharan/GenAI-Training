import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY is not set in the environment."
    )


# --------------------------------------------------
# OpenRouter configuration
# --------------------------------------------------

API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-4o-mini"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# --------------------------------------------------
# Load test cases
# --------------------------------------------------

def load_test_cases():
    """
    Load evaluation test cases from JSON file.
    """

    path = Path("tests/medication_cases.json")

    if not path.exists():
        raise FileNotFoundError(
            "tests/medication_cases.json not found."
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


# --------------------------------------------------
# Load prompt
# --------------------------------------------------

def load_prompt(version):
    """
    Load one prompt version.
    """

    path = Path(
        f"prompts/task_{version}.txt"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found."
        )

    return path.read_text(
        encoding="utf-8"
    )


# --------------------------------------------------
# Call OpenRouter
# --------------------------------------------------

def call_model(prompt):
    """
    Send prompt to OpenRouter and return
    the model's text response.
    """

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = httpx.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=30.0
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]


# --------------------------------------------------
# Clean model JSON response
# --------------------------------------------------

def clean_json(text):
    """
    Remove Markdown code fences if the model
    returns JSON inside ```json ... ```.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):]

    elif text.startswith("```"):
        text = text[len("```"):]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# --------------------------------------------------
# Evaluate one response
# --------------------------------------------------

def evaluate_response(actual, expected):
    """
    Compare the model's JSON output with the
    expected JSON output.

    Returns:
        True  -> correct
        False -> incorrect
    """

    try:
        cleaned = clean_json(actual)

        actual_json = json.loads(cleaned)

        return actual_json == expected

    except json.JSONDecodeError:
        return False


# --------------------------------------------------
# Evaluate one prompt version
# --------------------------------------------------

def evaluate_version(version, test_cases):
    """
    Run all test cases against one prompt version.
    """

    print()
    print("=" * 60)
    print(f"TESTING {version.upper()}")
    print("=" * 60)

    prompt_template = load_prompt(version)

    passed = 0
    total = len(test_cases)

    for index, case in enumerate(test_cases, start=1):

        print()
        print(f"Test Case {index}")
        print("-" * 40)

        prompt = prompt_template.replace(
            "{note}",
            case["note"]
        )

        actual = call_model(prompt)

        expected = case["expected"]

        is_correct = evaluate_response(
            actual,
            expected
        )

        if is_correct:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"Status: {status}")

        print("\nExpected:")
        print(
            json.dumps(
                expected,
                indent=2
            )
        )

        print("\nActual:")
        print(actual)

    score = (passed / total) * 100

    print()
    print("-" * 60)
    print(f"{version.upper()} RESULT")
    print("-" * 60)
    print(f"Passed : {passed}/{total}")
    print(f"Score  : {score:.2f}%")

    return score


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 60)
    print("        PROMPT EVALUATION")
    print("=" * 60)

    test_cases = load_test_cases()

    versions = [
        "v1",
        "v2",
        "v3",
        "v4",
        "v5"
    ]

    scores = {}

    for version in versions:

        score = evaluate_version(
            version,
            test_cases
        )

        scores[version] = score

    # --------------------------------------------------
    # Final comparison
    # --------------------------------------------------

    print()
    print()
    print("=" * 60)
    print("FINAL PROMPT COMPARISON")
    print("=" * 60)

    for version, score in scores.items():

        print(
            f"{version.upper():<5} -> {score:.2f}%"
        )

    best_version = max(
        scores,
        key=scores.get
    )

    print()
    print("-" * 60)
    print(
        f"BEST PROMPT: {best_version.upper()}"
    )
    print(
        f"SCORE: {scores[best_version]:.2f}%"
    )
    print("-" * 60)


if __name__ == "__main__":
    main()