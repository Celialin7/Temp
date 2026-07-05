"""
Compliance discussion-point evaluator for a single call transcript vs one standard script.

Pipeline: compress transcript -> overlapping dialogue chunks -> embedding retrieval -> GPT evaluation.
Edit the User settings section below before running.
"""

import json
import re
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# --- User settings (edit before running) ---
CALL_CSV_PATH = "path/to/your/transcript.csv"
SCRIPT_XLSX_PATH = "path/to/your/script.xlsx"
OUTPUT_CSV_PATH = "path/to/save/result.csv"

# Optional tuning
CHUNK_SIZE = 6
CHUNK_OVERLAP = 2
TOP_K = 6
SPEAKER_COL = "Speaker Roles"
TEXT_COL = "Transcription"


def call_text_embedding_3_small(text: str) -> dict:
    """Return OpenAI-style response: {"data": [{"embedding": [...]}]}"""
    raise NotImplementedError("Wire up your embedding API call here")


def call_gpt5nano(prompt: str) -> dict:
    """Return OpenAI-style chat response with choices[0].message.content as JSON string."""
    raise NotImplementedError("Wire up your GPT API call here")


def compress_transcript(df: pd.DataFrame) -> List[str]:
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

    return turns


def build_chunks(
    turns: List[str],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[Tuple[int, str]]:
    """Split turns into overlapping dialogue chunks; returns (start_turn_idx, chunk_text)."""
    if not turns:
        return []

    if len(turns) <= chunk_size:
        return [(0, "\n".join(turns))]

    step = max(1, chunk_size - overlap)
    chunks: List[Tuple[int, str]] = []
    for start in range(0, len(turns), step):
        end = min(start + chunk_size, len(turns))
        chunks.append((start, "\n".join(turns[start:end])))
        if end >= len(turns):
            break

    return chunks


def embed_text(text: str) -> np.ndarray:
    """Call embedding API and return a 1D numpy vector."""
    result = call_text_embedding_3_small(text)
    return np.array(result["data"][0]["embedding"], dtype=float)


def retrieve_top_chunks(
    query_text: str,
    chunks: List[Tuple[int, str]],
    chunk_embeddings: np.ndarray,
    k: int = TOP_K,
) -> List[str]:
    """Retrieve top-k similar chunks by cosine similarity, returned in transcript order."""
    if not chunks:
        return []

    query_emb = embed_text(query_text).reshape(1, -1)
    scores = cosine_similarity(query_emb, chunk_embeddings)[0]
    k = min(k, len(chunks))
    top_indices = np.argsort(scores)[-k:][::-1]

    selected = sorted((chunks[i] for i in top_indices), key=lambda item: item[0])
    return [text for _, text in selected]


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
            "reason": f"Invalid JSON from GPT: {exc}",
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
    retrieved_chunks: List[str],
) -> dict:
    """Ask GPT whether the discussion point is covered based on retrieved transcript chunks."""
    chunks_block = "\n\n".join(
        f"[Chunk {idx}]\n{chunk}" for idx, chunk in enumerate(retrieved_chunks, start=1)
    )
    if not chunks_block:
        chunks_block = "(No transcript chunks retrieved.)"

    prompt = f"""You are an experienced compliance auditor.

Task: Determine whether the sales agent covered the required discussion point in the call transcript excerpts below.

Rules:
- Accept paraphrased wording if the meaning matches.
- Treat Standard Written Chinese and spoken Cantonese as equivalent when they express the same meaning.
- Ignore incorrect speaker labels if conversational context clearly indicates the sales agent delivered the message.
- Base your judgement ONLY on the supplied transcript chunks.
- Return ONLY valid JSON with keys: point_id, status, reason.
- status must be exactly "Covered" or "Not Covered".

Required_Discussion_Point:
{required_point}

Standard_Script:
{standard_script}

Retrieved transcript chunks (chronological):
{chunks_block}

Return JSON example:
{{"point_id": {point_id}, "status": "Covered", "reason": "Sales explained surrender charges using colloquial Cantonese."}}
"""

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

    print("Step 1: Compressing transcript...")
    turns = compress_transcript(call_df)
    print(f"  {len(turns)} dialogue turns after compression")

    print("Step 2: Building overlapping chunks...")
    chunks = build_chunks(turns)
    print(f"  {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    print("Step 3: Embedding transcript chunks...")
    chunk_embeddings = np.vstack([embed_text(text) for _, text in chunks])

    results = []
    total = len(script_df)
    print("Step 4: Evaluating discussion points...")
    for idx, row in script_df.iterrows():
        point_id = idx + 1
        required_point = str(row["Required_Discussion_Point"])
        standard_script = str(row["Standard_Script"])
        print(f"  Evaluating point {point_id}/{total}...")

        retrieved = retrieve_top_chunks(standard_script, chunks, chunk_embeddings, k=TOP_K)
        evaluation = evaluate_point(point_id, required_point, standard_script, retrieved)

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
