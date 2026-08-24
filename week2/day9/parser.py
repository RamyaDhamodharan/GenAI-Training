import json
import re


def clean_response(raw: str) -> str:
    raw = raw.strip()

    # Remove markdown JSON fence
    if raw.startswith("```json"):
        raw = raw[7:]

    # Remove closing markdown fence
    if raw.endswith("```"):
        raw = raw[:-3]

    # Remove prose before JSON
    start = raw.find("{")

    if start != -1:
        raw = raw[start:]

    # Remove trailing commas before } or ]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)

    return raw.strip()


def parse_json_response(raw: str) -> dict:
    cleaned = clean_response(raw)
    return json.loads(cleaned)