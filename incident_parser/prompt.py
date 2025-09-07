# prompt.py
from typing import List, Dict, Optional

SYSTEM_INSTRUCTIONS = (
    "You are an incident-extraction assistant. Read the provided transcript and extract the requested fields. "
    "Return ONLY a single valid JSON object (no code fences, no explanation, no extra text). "
    "The JSON must use double quotes for keys and values, contain EXACTLY the requested keys, and each value must be a string."
)

field_descriptions = {
    "fire_suppression_appliance": "Appliance(s) used to suppress the fire (e.g., engine, ladder).",
    "fire_water_supply": "Type or source of water used at the incident (e.g., hydrant, tanker).",
    "fire_investigation_need": "Whether a formal fire investigation was judged necessary.",
    "fire_investigation_type": "Category or type of investigation conducted (if any).",
    "structure_arrival_conditions": "Fire conditions observed when responders arrived.",
    "structure_progression_conditions": "Whether the fire progressed beyond arrival conditions.",
    "structure_damage": "Extent or rating of damage to the building of origin.",
    "structure_floor_of_origin": "Floor or story where the fire originated.",
    "structure_room_of_origin": "Room or area where the fire started.",
    "structure_fire_cause": "Likely or determined cause of the structure fire.",
    "outside_fire_cause": "Likely or determined cause of the outdoor fire.",
    "outside_fire_acres_burned": "Estimated number of acres burned in the outdoor fire."
}

def build_extraction_prompt(
    transcript: str,
    fields: List[str],
    field_descriptions: Optional[Dict[str, str]] = None
) -> str:
    
    # Format the wanted fields as a JSON array string
    wanted_json_array = "[" + ", ".join(f"\"{f}\"" for f in fields) + "]"

    # If descriptions provided, format as compact bullet list (so we can merge it into the prompt)
    desc_block = ""
    if field_descriptions:
        lines = []
        for f in fields:
            if f in field_descriptions:
                # single-line description
                d = field_descriptions[f].strip().replace("\n", " ")
                lines.append(f'"{f}": {d}')
        if lines:
            desc_block = "FIELD DESCRIPTIONS (use these formats):\n" + "\n".join(lines) + "\n\n"

    return f"""{SYSTEM_INSTRUCTIONS}

Requested fields (exact keys):
{wanted_json_array}

{desc_block}RULES (follow exactly):
1. Output: A SINGLE compact JSON object and NOTHING else. Example: {{"example_key":"value"}}.
2. The JSON MUST contain EXACTLY the keys listed above (same spelling).
3. Each key's value MUST be a JSON string. If the field is not present, set its value to an empty string: "".
4. Do NOT add any additional keys, metadata, confidence scores, comments, or surrounding text.
5. Keep values short and factual (one line). Collapse newlines and excessive whitespace into single spaces.
6. Booleans -> "true"/"false". Numbers -> string (e.g., "3"). Lists -> items joined by "; ".
7. If multiple candidates exist, choose the first clear explicit mention.
8. Output must be compact (single line).

TRANSCRIPT:
{transcript}
"""
