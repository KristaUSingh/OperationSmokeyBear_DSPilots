# demo.py
import os
from incident_parser.categorize import categorize_transcript
from incident_parser.providers import GeminiProvider  # or use your _default_provider()

# Make sure your Gemini key is available:
# export GOOGLE_API_KEY="your_key"

# Pick the fields you want to fill in your NERIS form (tweak as needed)
NERIS_FIELDS = [
    "incident_final_type",         # e.g., "Fire / Structure Fire"
    "incident_special_modifier",   # e.g., "2nd alarm", "MCI"
    "tactic_timestamps",           # short text or "alarm:14:03; on_scene:14:07"
    "incident_location",           # short address or intersection
    "unit_response",               # short: "E201 on_scene 19:47; L107 ventilated"
    "incident_actions_taken",      # short: "fire attack; ventilation; overhaul"
    "medical",                     # short summary: "1 adult smoke inhalation refused transport"
    "incident_rescue_animal",      # "1" or ""
    "incident_narrative_impediment",# short: "hydrant low pressure"
    "incident_narrative_outcome",  # short: "fire under control; building evacuated"
    "incident_aid_direction",      # "received"|"given"|"none"
    "incident_aid_department_name", # short list string or ""
    "narrative"
]

# Example written transcript (paste a real radio/incident narrative here)
sample_transcript = """
Dispatch at 19:42 for a reported kitchen fire at 1287 Maple Ave, Queens, NY 11432.
E201 on scene at 19:47, light smoke showing from a two-story private dwelling. 
Crew advanced a 1¾” line to first-floor kitchen, fire confined to stovetop and adjacent cabinets.
Primary search negative. Ventilation by L107. Fire under control at 19:55. 
Likely cause: unattended cooking; pan of oil ignited. No sprinklers. Smoke alarm sounded.
One adult resident with mild smoke inhalation refused transport. No firefighter injuries.
"""

def main():
    provider = GeminiProvider(model_name="gemini-2.5-flash-lite", temperature=0.0)
    result = categorize_transcript(sample_transcript, NERIS_FIELDS, provider=provider)
    # Pretty-print
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()