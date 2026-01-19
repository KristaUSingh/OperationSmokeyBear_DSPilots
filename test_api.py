import requests
import json

transcript = """
Engine 201 responded to a reported kitchen fire at 1287 Maple Ave. 
Light smoke was showing from a two-story private home on arrival. 
Crew advanced a 1¾ inch hose line into the first-floor kitchen where 
flames were found on the stovetop and nearby cabinets. Fire was 
extinguished with water, and cabinets were overhauled to ensure no 
hidden fire. Ventilation performed by Truck 107. Cause determined 
to be unattended cooking oil. Smoke alarm activated and warned 
residents. One adult resident evaluated for smoke inhalation but 
refused transport. No firefighter injuries.
"""

print("Sending request... (will take 60-90 seconds)")
response = requests.post(
    "http://159.203.114.11/categorize-transcript",
    json={"transcript": transcript},
    timeout=120
)

# Pretty print the response
fields = response.json()["fields"]
print("\n✅ Extracted Fields:")
for key, value in fields.items():
    if value["value"]:  # Only show non-empty fields
        print(f"  {key}: {value['value']} (confidence: {value['confidence']})")