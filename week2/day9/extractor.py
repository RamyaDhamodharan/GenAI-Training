import ollama

from models import Medication
from parser import parse_json_response


MODEL_NAME = "qwen3:4b"


def call_model(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def validate_response(raw: str) -> Medication:
    data = parse_json_response(raw)

    return Medication(**data)


def extract_medication(text: str) -> Medication | None:

    prompt = f"""
Extract the medication information from the text below.

Return ONLY JSON.

The JSON must have this structure:

{{
    "name": "string",
    "dose": "string or null"
}}

Text:
{text}
"""

    # -------------------------
    # First attempt
    # -------------------------

    first_response = call_model(prompt)

    try:
        medication = validate_response(first_response)

        return medication

    except Exception as error:

        print("First attempt failed.")
        print("Error:", error)
        print("Retrying once...")

    # -------------------------
    # Retry
    # -------------------------

    retry_prompt = f"""
Your previous response could not be parsed or validated.

The error was:

{error}

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "name": "string",
    "dose": "string or null"
}}

Do not add:
- Markdown fences
- Explanations
- Extra text
- Comments

Original text:

{text}
"""

    retry_response = call_model(retry_prompt)

    try:
        medication = validate_response(retry_response)

        return medication

    except Exception as retry_error:

        print("Retry failed.")
        print("Error:", retry_error)

        return None


# -------------------------
# Main program
# -------------------------

if __name__ == "__main__":

    text = "The patient was prescribed Paracetamol 500 mg twice daily."

    medication = extract_medication(text)

    if medication:

        print("\nFinal result:")
        print(medication)

    else:

        print("\nExtraction failed cleanly.")