# demo_prompted.py
import json
from incident_parser.categorize import categorize_transcript
from incident_parser.providers import GeminiProvider

sample_transcript = """
Dispatch at 19:42 for a reported kitchen fire at 1287 Maple Ave, Queens, NY 11432.
E201 on scene at 19:47, light smoke showing from a two-story private dwelling. 
The weather is clear, 75°F, wind calm.
Crew advanced a 1¾” line to first-floor kitchen, fire confined to stovetop and adjacent cabinets.
Primary search negative. Ventilation by L107. Fire under control at 19:55. 
Likely cause: unattended cooking; pan of oil ignited. No sprinklers. Smoke alarm sounded.
One adult resident with mild smoke inhalation refused transport. No firefighter injuries.
"""


def main():
    provider = GeminiProvider(model_name="gemini-2.5-flash-lite", temperature=0.0)
    # pass the combined prompt to categorize_transcript if supported by your backend
    result = categorize_transcript(
        sample_transcript,
        provider=provider
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()