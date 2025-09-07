#prompt.py
from typing import List

SYSTEM_INSTRUCTIONS = (
    "You are an incident extractor for fire incident response forms. Read the transcript and extract the requested fields."
    "Return ONLY one JSON object with EXACTLY the requested keys and string values ONLY. Do not include code blocks, comments, or extra keys."
)

def build_extraction_prompt(transcript: str, fields: List[str]) -> str:
    wanted = ", ".join(fields)
    return f"""
Extract the following fields and return a SINGLE compact JSON object with EXACTLY these keys:
[{wanted}]

Rules:
- Each key must map to a string value (use \"\" when absent).
- Do NOT include any additional keys.
- Do NOT include confidence, metadata, or commentary.
- Avoid long prose; keep values short and factual (1 line each).
- Use the transcript text only; do not invent facts.

TRANSCRIPT:
{transcript}
"""
