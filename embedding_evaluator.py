"""
Embedding-only compliance evaluator for one call transcript vs one standard script.

Pipeline: compress transcript -> overlapping chunks -> cosine similarity vs Standard_Script.
Edit the User settings section below before running.
"""

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# --- User settings (edit before running) ---
CALL_CSV_PATH = "path/to/your/transcript.csv"
SCRIPT_XLSX_PATH = "path/to/your/script.xlsx"
OUTPUT_CSV_PATH = "path/to/save/result.csv"

SIMILARITY_THRESHOLD = 0.75

CHUNK_SIZE = 6
CHUNK_OVERLAP = 2
SPEAKER_COL = "Speaker Roles"
TEXT_COL = "Transcription"


def call_text_embedding_3_small(text: str) -> dict:
    """Return OpenAI-style response: {"data": [{"embedding": [...]}]}"""
    raise NotImplementedError("Wire up your embedding API call here")


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
    result = call_text_embedding_3_small(text)
    return np.array(result["data"][0]["embedding"], dtype=float)


def find_best_match(
    script_text: str,
    chunks: List[Tuple[int, str]],
    chunk_embeddings: np.ndarray,
) -> Tuple[float, str]:
    """Return highest cosine similarity score and its matched chunk text."""
    if not chunks:
        return 0.0, ""

    script_emb = embed_text(script_text).reshape(1, -1)
    scores = cosine_similarity(script_emb, chunk_embeddings)[0]
    best_idx = int(np.argmax(scores))
    return float(scores[best_idx]), chunks[best_idx][1]


def main() -> None:
    print("Loading inputs...")
    call_df = pd.read_csv(CALL_CSV_PATH)
    script_df = pd.read_excel(SCRIPT_XLSX_PATH)

    for col in ("Required_Discussion_Point", "Standard_Script"):
        if col not in script_df.columns:
            raise ValueError(f"Script file missing column: {col}")

    print("Compressing transcript...")
    turns = compress_transcript(call_df)
    print(f"  {len(turns)} dialogue turns")

    print("Building overlapping chunks...")
    chunks = build_chunks(turns)
    print(f"  {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    print("Embedding transcript chunks...")
    chunk_embeddings = np.vstack([embed_text(text) for _, text in chunks])

    results = []
    total = len(script_df)
    print("Evaluating discussion points...")
    for idx, row in script_df.iterrows():
        point_id = idx + 1
        required_point = str(row["Required_Discussion_Point"])
        standard_script = str(row["Standard_Script"])
        print(f"  Point {point_id}/{total}...")

        score, matched_chunk = find_best_match(standard_script, chunks, chunk_embeddings)
        status = "Covered" if score >= SIMILARITY_THRESHOLD else "Not Covered"

        results.append(
            {
                "point_id": point_id,
                "Required_Discussion_Point": required_point,
                "similarity_score": round(score, 4),
                "matched_chunk": matched_chunk,
                "status": status,
            }
        )

    output_df = pd.DataFrame(results)
    print("\nResults:")
    print(output_df.to_string(index=False))

    output_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"\nSaved results to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
