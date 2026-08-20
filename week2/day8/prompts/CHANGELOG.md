task_v1.txt
Extract medications from the following note:


{note}
task_v2.txt
Extract medications from the following note:


{note}


Return the result as a JSON array.

Only change from V1: Added JSON output instruction.

task_v3.txt
Extract medications from the following note:


{note}


Return the result as a JSON array.


Use only information provided in the note.

Only change from V2: Added the constraint to use only the note.

task_v4.txt
Extract medications from the following note:


{note}


Return the result as a JSON array.


Use only information provided in the note.


Example:
Note: Patient takes Aspirin 100 mg daily.
Output: [{"name": "Aspirin", "dose": "100 mg", "frequency": "daily"}]

Only change from V3: Added one few-shot example.

task_v5.txt
Extract medications from the following note:


{note}


Return the result as a JSON array.


Use only information provided in the note.


Example:
Note: Patient takes Aspirin 100 mg daily.
Output: [{"name": "Aspirin", "dose": "100 mg", "frequency": "daily"}]


For every medication, infer the most likely intended dose and frequency when information is incomplete.

Only change from V4: Added the inference instruction.

This is intentionally the potentially bad change because it can encourage the model to guess missing information.


# Prompt Iteration Log

## Task

Extract medication information from a medical note.

Test input used for all versions:

Patient takes Paracetamol 500 mg twice daily.

Expected output:

[
  {
    "name": "Paracetamol",
    "dose": "500 mg",
    "frequency": "twice daily"
  }
]

---

## V1

- Change: Baseline prompt with no additional instructions.
- Expected: Extract medication information from the note.
- Actual:

The model returned:

The medication extracted from the note is:

- Paracetamol 500 mg, taken twice daily.

- Result: The medication information was extracted correctly, but the response was plain text instead of structured JSON.

---

## V2

- Change: Added JSON array output format.
- Expected: The model should return the extracted medications as JSON.
- Actual:

[
    {
        "medication": "Paracetamol",
        "dosage": "500 mg",
        "frequency": "twice daily"
    }
]

- Result: The model returned JSON, but the field names did not match the expected schema. It used `medication` and `dosage` instead of `name` and `dose`.

---

## V3

- Change: Added a constraint to use only information from the note.
- Expected: The model should avoid inventing missing information.
- Actual:

[
    {
        "medication": "Paracetamol",
        "dose": "500 mg",
        "frequency": "twice daily"
    }
]

- Result: The output remained JSON and the `dose` field matched the expected name, but the medication field was still `medication` instead of `name`.

---

## V4

- Change: Added one few-shot example.
- Expected: The model should follow the expected extraction pattern more consistently.
- Actual:

[
    {
        "name": "Paracetamol",
        "dose": "500 mg",
        "frequency": "twice daily"
    }
]

- Result: The model followed the example and returned the expected field names and JSON structure. This was the best result among the tested versions.

---

## V5

- Change: Added an instruction to infer missing medication details.
- Expected: The model might provide more complete-looking results.
- Actual:

[
    {
        "medication": "Paracetamol",
        "dose": "500 mg",
        "frequency": "twice daily"
    }
]

- Result: The output became worse compared with V4 because the model changed the expected `name` field back to `medication`. The additional inference instruction did not improve the output and introduced a regression.

- Failed version: Yes. V5 is intentionally kept as the failed version required by the task.

---

## Summary

| Version | Change | Result |
|---|---|---|
| V1 | Baseline prompt | Correct information, but plain text |
| V2 | Added JSON array format | JSON output, but incorrect field names |
| V3 | Added note-only constraint | JSON output improved, but medication field was still incorrect |
| V4 | Added one few-shot example | Correct JSON structure and field names |
| V5 | Added inference instruction | Regression; output became worse than V4 |

---

## Conclusion

The prompt was iteratively improved through five versions.

Each version introduced one intended change.

V1 established the baseline behavior.

V2 improved the output format by requesting a JSON array.

V3 added a constraint to use only information from the provided note.

V4 added a few-shot example, which improved consistency and produced the expected field names.

V5 added an instruction to infer missing medication details. This change caused a regression in the tested output, making V5 worse than V4.

The failed V5 version was intentionally retained to demonstrate that prompt changes must be tested and that not every prompt modification improves model performance.

V1 → baseline
V2 → + JSON format
V3 → + constraint
V4 → + one example
V5 → + inference instruction
