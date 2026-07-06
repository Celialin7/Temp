"""
GPT-only compliance evaluator for one call transcript vs one standard script.

Pipeline: compress transcript -> GPT evaluation per discussion point (no embedding).
Edit the User settings section below before running.
"""

import json
import re
from typing import List

import pandas as pd

# --- User settings (edit before running) ---
CALL_CSV_PATH = "path/to/your/transcript.csv"
SCRIPT_XLSX_PATH = "path/to/your/script.xlsx"
OUTPUT_CSV_PATH = "path/to/save/result.csv"

SPEAKER_COL = "Speaker Roles"
TEXT_COL = "Transcription"


def call_gpt5nano(prompt: str) -> dict:
    """Return OpenAI-style chat response with choices[0].message.content as JSON string."""
    raise NotImplementedError("Wire up your GPT API call here")


def compress_transcript(df: pd.DataFrame) -> str:
    """Keep speaker + text columns, shorten speaker labels, merge consecutive same-speaker rows."""
    required = {SPEAKER_COL, TEXT_COL}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Call CSV missing columns: {sorted(missing)}")

    df = df[[SPEAKER_COL, TEXT_COL]].copy()
    df[TEXT_COL] = df[TEXT_COL].astype(str).str.strip()
    df = df[df[TEXT_COL].ne("") & df[TEXT_COL].ne("nan")]

    speaker_map = {}
    next_id = 1
    turns: List[str] = []

    for _, row in df.iterrows():
        speaker = str(row[SPEAKER_COL]).strip()
        text = row[TEXT_COL]
        if speaker not in speaker_map:
            speaker_map[speaker] = f"S{next_id}"
            next_id += 1
        short_speaker = speaker_map[speaker]

        if turns and turns[-1].startswith(f"{short_speaker}: "):
            turns[-1] = turns[-1] + " " + text
        else:
            turns.append(f"{short_speaker}: {text}")

    return "\n".join(turns)


def parse_gpt_json(content: str, point_id: int) -> dict:
    """Parse GPT JSON output with basic fence stripping and validation."""
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return {
            "point_id": point_id,
            "status": "Not Covered",
            "reason": f"Invalid JSON: {exc}",
        }

    status = data.get("status", "Not Covered")
    if status not in ("Covered", "Not Covered"):
        status = "Not Covered"

    return {
        "point_id": point_id,
        "status": status,
        "reason": str(data.get("reason", "")),
    }


def evaluate_point(
    point_id: int,
    required_point: str,
    standard_script: str,
    transcript: str,
) -> dict:
    """Ask GPT whether the discussion point appears in the compressed transcript."""
    prompt = f"""Compliance check. Does the transcript contain the required discussion point?
Paraphrases and equivalent Cantonese count as Covered. Do not infer missing info.
Return JSON only: {{"point_id": {point_id}, "status": "Covered" or "Not Covered", "reason": "short"}}

Required_Discussion_Point: {required_point}
Standard_Script: {standard_script}
Transcript:
{transcript}"""

    try:
        result = call_gpt5nano(prompt)
        content = result["choices"][0]["message"]["content"]
        return parse_gpt_json(content, point_id)
    except Exception as exc:
        return {
            "point_id": point_id,
            "status": "Not Covered",
            "reason": f"API error: {exc}",
        }


def main() -> None:
    print("Loading inputs...")
    call_df = pd.read_csv(CALL_CSV_PATH)
    script_df = pd.read_excel(SCRIPT_XLSX_PATH)

    for col in ("Required_Discussion_Point", "Standard_Script"):
        if col not in script_df.columns:
            raise ValueError(f"Script file missing column: {col}")

    print("Compressing transcript...")
    transcript = compress_transcript(call_df)
    print(f"  {len(transcript.splitlines())} dialogue turns")

    results = []
    total = len(script_df)
    print("Evaluating discussion points...")
    for idx, row in script_df.iterrows():
        point_id = idx + 1
        required_point = str(row["Required_Discussion_Point"])
        standard_script = str(row["Standard_Script"])
        print(f"  Point {point_id}/{total}...")

        evaluation = evaluate_point(point_id, required_point, standard_script, transcript)
        results.append(
            {
                "point_id": evaluation["point_id"],
                "Required_Discussion_Point": required_point,
                "status": evaluation["status"],
                "reason": evaluation["reason"],
            }
        )

    output_df = pd.DataFrame(results)
    print("\nResults:")
    print(output_df.to_string(index=False))

    output_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"\nSaved results to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
