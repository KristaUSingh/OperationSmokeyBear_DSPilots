# prompt.py
from typing import List, Dict, Optional

SYSTEM_INSTRUCTIONS = (
    "Return ONLY a single valid JSON object (no code fences, no explanation, no extra text). "
    "The JSON must use double quotes for keys and values, contain EXACTLY the requested keys, and each value must be an object with 'value' and 'confidence'. "
    "For example: {\"incident_type\":{\"value\":\"Fire\",\"confidence\":0.92}}."
)

field_descriptions = {
    "incident_neris_id": "NERIS-style incident id; provide matching format or an obvious placeholder if absent.",
    "incident_internal_id": "Local/internal incident id used by the department.",
    "incident_final_type": "Primary incident type(s) such as 'fire', 'medical', or 'hazsit'.",
    "incident_final_type_primary": "Primary incident type when multiple types are present.",
    "incident_special_modifier": "Any special modifiers (e.g., 'active assailant','mass_casualty_incident', 'FEDERAL_DECLARED_DISASTER').",
    "fire": "Whether this incident involved a fire ('true' or 'false' as strings).",
    "medical": "Whether this incident involved a medical event ('true' or 'false' as strings).",
    "hazsit": "Whether this incident was a hazardous situation ('true' or 'false' as strings).",
    "emerging_hazard": "Short description of any emerging hazard noted during the incident.",
    "tactic_timestamps": "Tactics used (e.g., 'ventilation; attack') optionally with nearby times; join items with '; '.",
    "incident_point": "Latitude and longitude in decimal degrees (WGS84) or empty string if unavailable.",
    "incident_polygon": "Incident polygon in WGS84 coordinates or empty string if unavailable.",
    "incident_location": "Address or description of incident location (street, city, ZIP).",
    "incident_location_use": "How the location was used (e.g., 'warehouse – storage').",
    "incident_people_present": "Whether people were present at time of incident ('true'/'false' as strings) or '' if unknown.",
    "incident_displaced_number": "Number of people displaced (integer as string, e.g. '3'; '' if unknown).",
    "incident_displaced_cause": "Reason people were displaced (e.g., 'evacuation due to smoke').",
    "exposure": "Details of exposures (people, buildings, or nearby property).",
    "rescue_ff": "Summary of firefighter rescues/casualties and counts (short text).",
    "rescue_nonff": "Summary of non-firefighter rescues/casualties (civilians/animals) and counts (short text).",
    "incident_rescue_animal": "Number of animals rescued (integer as string, e.g. '2'; '' if none/unknown).",
    "incident_actions_taken": "List actions taken by fire department, joined with '; ' (e.g., 'extinguish; ventilate; search').",
    "incident_noaction": "If no action was taken, brief reason ('' if not applicable).",
    "unit_response": "Units that responded with arrival times if given (e.g., 'E201 19:47; L107 19:50').",
    "risk_reduction": "Risk-reduction systems present and function (e.g., 'smoke alarm present and operated; no sprinklers').",
    "incident_aid_direction": "'given' or 'received' as a string, or '' if none/unknown.",
    "incident_aid_type": "Type of aid (e.g., 'mutual aid', 'automatic aid').",
    "incident_aid_department_name": "Name(s) of departments that gave or received aid (short list joined by '; ').",
    "incident_aid_nonfd": "Non-fire agencies that assisted (e.g., 'EMS; police'), joined by '; '.",
    "incident_narrative_impediment": "Any obstacles or impediments (e.g., 'blocked hydrant', 'heavy traffic').",
    "incident_narrative_outcome": "One-sentence summary of the incident outcome.",
    "parcel": "Parcel characteristics: property type, occupancy, and size if available (short).",
    "weather": "Brief weather summary during incident (temperature, wind, precipitation).",
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
1. Output: A SINGLE compact JSON object and NOTHING else.
   Example: {"incident_type":{"value":"Fire","confidence":0.92}}.
2. The JSON MUST contain EXACTLY the keys listed above (same spelling).
3. Each key's value MUST be an object containing:
   - "value": the extracted text as a string (or "" if not found)
   - "confidence": a number between 0.0 and 1.0 representing certainty
4. Do NOT add any keys other than "value" and "confidence" for each field.
5. Keep values short and factual (one line). Collapse newlines and excessive whitespace into single spaces.
6. Booleans -> "true"/"false". Numbers -> string (e.g., "3"). Lists -> items joined by "; ".
7. If multiple candidates exist, choose the first clear explicit mention.
8. Output must be compact (single line).

EXAMPLE:
Transcript: "There was a brush fire in Los Angeles that displaced three people."
Expected JSON:
{
  "incident_final_type": {"value": "fire", "confidence": 0.95},
  "incident_location": {"value": "Los Angeles", "confidence": 0.9},
  "incident_displaced_number": {"value": "3", "confidence": 0.92}
}

TRANSCRIPT:
{transcript}
"""
