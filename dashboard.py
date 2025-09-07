import streamlit as st
import pandas as pd
from datetime import datetime
from st_audiorec import st_audiorec
import whisper
import tempfile
import uuid
import os

st.set_page_config(page_title="Operation Smokey Bear", page_icon="🧑‍🚒", layout="wide")

# App Title 
st.title("WELCOME TO OPERATION SMOKEY BEAR 🔥🧸!")

# Master CSV setup
CSV_FILE = "incidents_master.csv"

# Load fire-specific columns from mod_fire.csv
fire_columns = pd.read_csv("mod_fire.csv")["name"].dropna().tolist()

# 33 column schema 
COLUMNS = [
    "incident_neris_id", "incident_internal_id", "incident_final_type",
    "incident_final_type_primary", "incident_special_modifier", "fire", "medical",
    "hazsit", "emerging_hazard", "tactic_timestamps", "incident_status",
    "incident_property_loss_value", "incident_property_loss_value_code",
    "incident_property_loss_comments", "incident_contents_loss_value",
    "incident_contents_loss_value_code", "incident_contents_loss_comments",
    "incident_casualties", "incident_fatalities", "incident_injuries",
    "incident_civ_casualties", "incident_civ_fatalities", "incident_civ_injuries",
    "incident_ff_casualties", "incident_ff_fatalities", "incident_ff_injuries",
    "incident_casualties_comments", "incident_response_time", "incident_departments",
    "incident_units", "incident_personnel", "incident_geolocation", "incident_address"
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
    if st.button("Parse incident"):
        # Basic parsing placeholder → fill only some columns, leave others blank
        parsed = {col: None for col in COLUMNS}
        parsed["incident_neris_id"] = f"INC-{uuid.uuid4().hex[:6]}"
        parsed["incident_final_type"] = "Structure Fire" if "fire" in incident_text.lower() else "Unknown"
        parsed["incident_address"] = "123 Main St" if "main" in incident_text.lower() else ""
        parsed["incident_injuries"] = "0"
        parsed["incident_casualties_comments"] = incident_text
        parsed["incident_status"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.session_state["parsed"] = parsed
        st.success("Incident parsed! Check the Review tab.")


# Tab 2: Review & Save 
with tab2:
    st.header("Please review parsed incident details")
    st.subheader("Edit fields if needed, then lock them before saving")

    st.divider()

    if "parsed" not in st.session_state:
        st.info("No parsed incident yet. Go to 'Record / Input' tab first.")
    else:
        parsed = st.session_state["parsed"]

        # Initialize correction state
        if "corrections" not in st.session_state:
            st.session_state["corrections"] = {col: False for col in ALL_COLUMNS}

        # Helper to render field
        def render_field(col, prefix=""):
            locked = st.session_state["corrections"].get(col, False)

            # Text input (disabled if locked)
            value = st.text_input(
                col,
                value=parsed.get(col, ""),
                disabled=locked,
                key=f"{prefix}input_{col}"
            )
            parsed[col] = value

            # Checkbox appears below the field
            lock_state = st.checkbox(
                f"Lock {col}",
                value=locked,
                key=f"{prefix}lock_{col}"
            )
            st.session_state["corrections"][col] = lock_state

        # Core fields
        st.subheader("Core Incident Fields")
        for col in COLUMNS:
            render_field(col)
        
        st.divider()

        # Fire fields (only if fire flagged)
        if parsed.get("fire") in ["Yes", "True", 1]:
            st.subheader("🔥 Fire-Specific Fields")
            for col in fire_columns:
                render_field(col, prefix="fire_")

        # Save button (enabled only if all required fields are locked)
        required_fields = COLUMNS + (fire_columns if parsed.get("fire") in ["Yes", "True", 1] else [])
        all_locked = all(st.session_state["corrections"].get(col, False) for col in required_fields)

        if st.button("Save to CSV", disabled=not all_locked):
            save_incident(parsed)
            st.success("Incident saved to CSV!")


# Tab 3: Dashboard 
with tab3:
    st.header("Incident Dashboard")

    st.divider()

    df = pd.read_csv(CSV_FILE)

    # Enforce schema with ALL columns
    for col in ALL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[ALL_COLUMNS]

    if df.empty:
        st.info("No incidents yet. Add one to see the dashboard.")
    else:
        # Show Core Incidents (33 columns)
        st.subheader("Core Incident Data (33 Columns)")
        st.dataframe(df[COLUMNS])
        st.bar_chart(df["incident_final_type"].value_counts())


        # Show Fire-Specific Incidents
        if "fire" in df.columns:
            fire_df = df[df["fire"].isin(["Yes", "True", 1])][fire_columns]

            if not fire_df.empty:
                st.divider()
                st.subheader("🔥 Fire-Specific Incident Data")
                st.dataframe(fire_df)
