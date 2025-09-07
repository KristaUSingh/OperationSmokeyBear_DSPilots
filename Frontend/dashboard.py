import streamlit as st
import pandas as pd
from datetime import datetime
from st_audiorec import st_audiorec
import whisper
import requests
import tempfile
import uuid
import os

st.set_page_config(page_title="Operation Smokey Bear", page_icon="🧑‍🚒", layout="wide")

# App Title 
st.title("WELCOME TO OPERATION SMOKEY BEAR 🔥🧸!")

# Master CSV setup
CSV_FILE = "incidents_master.csv"

# Load fire-specific columns from mod_fire.csv
fire_columns = pd.read_csv("Frontend/mod_fire.csv")["name"].dropna().tolist()

# 33 column schema 
COLUMNS = [
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
  "weather"
]

# Master schema = 33 core + fire-specific
ALL_COLUMNS = COLUMNS + fire_columns


if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=ALL_COLUMNS).to_csv(CSV_FILE, index=False)

def save_incident(data):
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Tabs
tab1, tab2, tab3 = st.tabs(["🎙️ Record / Input", "🧾 Review & Save", "📊 Dashboard"])

# Tab 1: Record / Input
with tab1:
    st.header("Record or enter incident details")

    st.divider()

    wav_audio_data = st_audiorec()  # returns recorded audio as wav byte stream

    incident_text = ""

    if wav_audio_data is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(wav_audio_data)
            audio_path = f.name

        # 🔊 Local Whisper transcription
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        incident_text = result["text"]

        st.write("Transcript:", incident_text)
        st.success("Audio transcribed successfully (Whisper local)!")

    else:
        incident_text = st.text_area("Or type/paste the incident description:")

    # Parse incident button
    if st.button("Parse incident") and incident_text.strip():
        try:
            response = requests.post(
                "http://127.0.0.1:8000/categorize-transcript",
                json={"transcript": incident_text},
                timeout=30
            )

            if response.status_code == 200:
                parsed = response.json().get("fields", {})
                st.session_state["parsed"] = parsed
                st.success("Incident parsed via backend! Check the Review tab.")
            else:
                st.error(f"Backend error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")



# Tab 2: Review & Save 
with tab2:
    st.header("Please review parsed incident details")
    st.subheader("Edit fields if needed, then approve before saving")

    st.divider()

    if "parsed" not in st.session_state:
        st.info("No parsed incident yet. Go to 'Record / Input' tab first.")
    else:
        parsed = st.session_state["parsed"]

        # Core fields
        st.subheader("Core Incident Fields")
        for col in COLUMNS:
            value = st.text_input(
                col,
                value=parsed.get(col, ""),
                key=f"input_{col}"
            )
            parsed[col] = value



        # Fire fields (auto-appear if fire flagged)
        if str(parsed.get("fire", "")).lower() in ["yes", "true", "1"]:
            st.divider()
            st.subheader("🔥 Fire-Specific Fields")
            for col in fire_columns:
                # If backend didn’t send this column, fall back to empty string
                value=parsed.get(col) if col in parsed else ""
                value = st.text_input(
                    col,
                    value=value,
                    key=f"input_fire_{col}"
                )
                parsed[col] = value

        # One approval checkbox at the end
        approved = st.checkbox("I approve this form, it is correct")

        if st.button("Save to CSV", disabled=not approved):
            save_incident(parsed)
            st.success("Incident saved to CSV!")

with tab3:
    st.subheader("Incident Dashboard")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        # Enforce schema
        for col in COLUMNS + fire_columns:
            if col not in df.columns:
                df[col] = ""

        # Core view
        st.subheader("Core Incidents")
        st.dataframe(df[COLUMNS])

        # Fire-specific view (filter only incidents where fire is true-ish)
        fire_flagged = df[df["fire"].astype(str).str.lower().isin(["true", "yes", "1"])]
        if not fire_flagged.empty:
            st.subheader("Fire-Specific Incidents")
            st.dataframe(fire_flagged[fire_columns])
        else:
            st.info("No fire-specific incidents yet.")

        # Download combined CSV (core + fire fields together)
        st.subheader("Download Full Dataset")
        combined_csv = df[COLUMNS + fire_columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Combined CSV",
            data=combined_csv,
            file_name="incidents_master.csv",
            mime="text/csv"
        )
    else:
        st.info("No incidents yet. Add one to see the dashboard.")

