#categorize.py
from typing import Dict, List, Optional
from .transcribe import transcribe_audio
from .providers import LLMProvider, GeminiProvider
import os
from dotenv import load_dotenv
load_dotenv()

NERIS_FIELDS = [
  "incident_neris_id",
  "incident_internal_id",
  "incident_final_type",
  "incident_final_type_primary",
  "incident_special_modifier",
  "fire",
  "medical",
  "hazsit",
  "emerging_hazard",
  "tactic_timestamps",
  "incident_point",
  "incident_polygon",
  "incident_location",
  "incident_location_use",
  "incident_people_present",
  "incident_displaced_number",
  "incident_displaced_cause",
  "exposure",
  "rescue_ff",
  "rescue_nonff",
  "incident_rescue_animal",
  "incident_actions_taken",
  "incident_noaction",
  "unit_response",
  "risk_reduction",
  "incident_aid_direction",
  "incident_aid_type",
  "incident_aid_department_name",
  "incident_aid_nonfd",
  "incident_narrative_impediment",
  "incident_narrative_outcome",
  "parcel",
  "weather",
  # Fire-specific fields appended
  "fire_suppression_appliance",
  "fire_water_supply",
  "fire_investigation_need",
  "fire_investigation_type",
  "structure_arrival_conditions",
  "structure_progression_conditions",
  "structure_damage",
  "structure_floor_of_origin",
  "structure_room_of_origin",
  "structure_fire_cause",
  "outside_fire_cause",
  "outside_fire_acres_burned"
]

def _default_provider() -> LLMProvider:
    kind = (os.getenv("LLM_PROVIDER") or "gemini").lower()
    if kind == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown provider: {kind}")

def categorize_audio_file(
    audio_path: str,
    fields: List[str],
    transcribe_model: str = "base",
    provider: Optional[LLMProvider] = None,
) -> Dict[str, str]:
    if not fields:
        raise ValueError("Must provide at least one field name to extract.")
    transcript = transcribe_audio(audio_path, model_name=transcribe_model)
    if provider is None:
        provider = _default_provider()
    return provider.extract_fields(transcript, fields)


def categorize_transcript(
    transcript: str,
    fields: List[str] = NERIS_FIELDS,
    provider: Optional[LLMProvider] = None,
) -> Dict[str, str]:
    if provider is None:
        provider = _default_provider()
    return provider.extract_fields(transcript, fields)