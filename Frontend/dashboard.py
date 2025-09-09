import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from faster_whisper import WhisperModel
import requests
import time
import tempfile
import os

st.set_page_config(page_title="Operation Smokey Bear", page_icon="🧑‍🚒", layout="wide")

# ===== CSS THEME =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Roboto:wght@400;500&family=Exo+2:wght@600&display=swap');

/* ===== BACKGROUND ===== */
html, body, .stApp {
    background: radial-gradient(circle at top left, rgba(255,107,53,0.08), transparent 70%),
                radial-gradient(circle at bottom right, rgba(79,142,247,0.08), transparent 70%),
                #0E1117;
    font-family: 'Inter', sans-serif;
}

/* ===== TITLE ===== */
.app-title {
    text-align: center;
    font-family: 'Russo One', sans-serif;
    font-weight: 900;
    font-size: 3rem;
    letter-spacing: 2px;
    text-shadow: 0 0 25px #FF6B35, 0 0 50px rgba(255,107,53,0.7);
    margin-bottom: 0.8rem;
}

/* ===== SECTION HEADERS (subheaders like Incident Dashboard) ===== */
h2 {
    font-family: 'Russo One', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    color: #FFFFFF !important;
    text-shadow: 0 0 12px rgba(255,107,53,0.4);  /* subtle fire glow */
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
}
            
h3 {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    color: #FFFFFF !important;
    text-shadow: 0 0 12px rgba(255,107,53,0.4);  /* subtle fire glow */
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;      
}


/* ===== LIVE BADGE ===== */
.live-badge {
    margin-top: 1rem;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
    font-size: 14px;
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(255,76,76,0.1);
    animation: pulse 1.5s infinite;
}
.live-dot {
    width: 10px;
    height: 10px;
    background: #FF4C4C;
    border-radius: 50%;
    box-shadow: 0 0 10px #FF4C4C;
}
@keyframes pulse {
    0% { box-shadow: 0 0 5px rgba(255, 76, 76, 0.4); }
    50% { box-shadow: 0 0 15px rgba(255, 76, 76, 1); }
    100% { box-shadow: 0 0 5px rgba(255, 76, 76, 0.4); }
}

/* ===== TABS ===== */
.stTabs [role="tab"] p {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px;
}

.stTabs [role="tablist"] {
    margin-top: 1.5rem;
    gap: 1.5rem;
    border-bottom: none;
    justify-content: center;
}
.stTabs [role="tab"] {
    background: #1C1F26;
    padding: 0.6rem 1.2rem;
    border-radius: 10px;
    font-weight: 600;
    color: #A9A9A9;
    transition: all 0.3s ease;
}
.stTabs [role="tab"]:hover {
    color: white;
    background: #2a2f3a;
    transform: scale(1.05);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #FF6B35, #8B5E3C);
    color: white !important;
    box-shadow: 0 4px 15px rgba(255,107,53,0.6);
}


/* ===== SELECTBOX (dropdown) ===== */
.stSelectbox div[data-baseweb="select"] {
    background-color: #1C1F26 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Inter', sans-serif;
    padding: 6px 10px !important;
    box-shadow: none !important;
}

/* Kill the inner orange focus border inside selectbox */
.stSelectbox div[data-baseweb="select"]:focus-within {
    outline: none !important;
    box-shadow: none !important;
    border: 1px solid #FF6B35 !important; /* keep your outer fire border */
}

/* Dropdown menu (options) */
.stSelectbox div[data-baseweb="popover"] {
    background-color: #1C1F26 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

/* Each option in the dropdown */
.stSelectbox div[data-baseweb="option"] {
    background: transparent !important;
    color: white !important;
    font-family: 'Inter', sans-serif;
}

.stSelectbox div[data-baseweb="option"]:hover {
    background: rgba(255,107,53,0.2) !important;
}

/* Neutralize selectbox input field but keep functionality */
.stSelectbox input {
    color: transparent !important;   /* hide text */
    background: transparent !important;
    border: none !important;
    caret-color: transparent !important; /* hide cursor */
    width: 0 !important;   /* shrink it down */
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}


/* ===== INPUT FIELDS ===== */
textarea, input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    background: #1C1F26 !important;
    color: white !important;
    padding: 12px !important;
    font-family: 'Inter', sans-serif;
}
            
textarea:focus, input:focus {
    border: 1px solid #FF6B35 !important;
    box-shadow: 0 0 12px rgba(255,107,53,0.6) !important;
}

/* ===== BUTTONS ===== */
.stButton>button {
    width: 100% !important;
    padding: 0.8rem 1.2rem !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #FF6B35, #D64545) !important;
    font-weight: bold !important;
    color: white !important;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 25px rgba(255,107,53,0.9) !important;
}
            
/* ===== DOWNLOAD BUTTON ===== */
[data-testid="stDownloadButton"] button {
    width: 100% !important;
    padding: 0.8rem 1.2rem !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #FF6B35, #D64545) !important;
    font-weight: bold !important;
    color: white !important;
    transition: all 0.3s ease-in-out;
}

[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 25px rgba(255,107,53,0.9) !important;
}

            
/* ===== CARDS ===== */
.metric-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 1.2rem;
    margin-bottom: 3rem;
    border-radius: 15px;
    background: #1C1F26;
    box-shadow: 0 0 20px rgba(255,107,53,0.25);
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.3s ease-in-out;
    min-height: 120px;
}

.metric-card:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 0 35px rgba(255,107,53,0.45);
}

.metric-card h3 {
    margin: 0;
    font-family: 'Russo One', sans-serif;
    font-size: 1.4rem;
    color: white;
}

.metric-card p {
    margin: 0;
    font-size: 2rem;
    font-weight: bold;
    color: #FF6B35;
}
            
.metric-fire { border-left: 5px solid #FF6B35; }
.metric-medical { border-left: 5px solid #4CAF50; }
.metric-hazmat { border-left: 5px solid #FFEB3B; }

/* ===== TABLES ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

/* Table headers */
[data-testid="stDataFrame"] thead tr th {
    background: #FF6B35 !important;
    color: white !important;
    font-weight: 600 !important;
    font-family: 'Exo 2', sans-serif;
    text-transform: uppercase;
    font-size: 0.9rem;
}

/* Table rows */
[data-testid="stDataFrame"] tbody tr td {
    background: #1C1F26 !important;
    color: white !important;
    font-size: 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}

/* Hover effect */
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(255,107,53,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown(
    """
    <div class="app-title">WELCOME TO OPERATION SMOKEY BEAR 🔥🧸!</div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display:flex;justify-content:center;margin-top:-10px;margin-bottom:20px;">
        <div class="live-badge">
            <div class="live-dot"></div>
            LIVE – Incident Speech-to-Text Tool
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ===== MAIN APP LOGIC =====
CSV_FILE = "incidents_master.csv"
fire_columns = pd.read_csv("Frontend/mod_fire.csv")["name"].dropna().tolist()

COLUMNS = [
  "incident_neris_id","incident_internal_id","incident_final_type","incident_final_type_primary",
  "incident_special_modifier","fire","medical","hazsit","emerging_hazard","tactic_timestamps",
  "incident_point","incident_polygon","incident_location","incident_location_use","incident_people_present",
  "incident_displaced_number","incident_displaced_cause","exposure","rescue_ff","rescue_nonff",
  "incident_rescue_animal","incident_actions_taken","incident_noaction","unit_response","risk_reduction",
  "incident_aid_direction","incident_aid_type","incident_aid_department_name","incident_aid_nonfd",
  "incident_narrative_impediment","incident_narrative_outcome","parcel","weather"
]

# ===== Sample Audio Files =====
SAMPLE_AUDIO = {
    "Sample Audio #1": "Frontend/sample_audio/sample_audio#1.m4a",
    "Sample Audio #2": "Frontend/sample_audio/sample_audio#2.m4a",
    "Sample Audio #3": "Frontend/sample_audio/sample_audio#3.m4a",
    "Sample Audio #4": "Frontend/sample_audio/sample_audio#4.m4a"
}


ALL_COLUMNS = COLUMNS + fire_columns
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=ALL_COLUMNS).to_csv(CSV_FILE, index=False)

def save_incident(data):
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["🎙️ Record / Input", "🧾 Review & Save", "📊 Dashboard"])

with tab1:
    st.header("Record or enter incident details")
    st.markdown("### 🎤 Tap to Start Live Recording", unsafe_allow_html=True)

    # Mic Button Wrapper
    audio = mic_recorder(
        start_prompt="▶️ Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True,
    )

    incident_text = ""
    if audio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio["bytes"])
            audio_path = f.name
        st.audio(audio["bytes"], format="audio/wav")

        model = WhisperModel("base", device="cpu")
        segments, _ = model.transcribe(audio_path)
        transcript = " ".join([segment.text for segment in segments])
        st.session_state["incident_text"] = transcript  
        st.write("Transcript:", transcript)
        st.success("Audio transcribed successfully!")

    # ===== Pre-Recorded Audio =====
    st.markdown("### Or select one of the following:")
    selected_audio = st.selectbox("Choose a sample audio:", ["None"] + list(SAMPLE_AUDIO.keys()))

    if selected_audio != "None":
        if st.button("Transcribe Selected Audio"):
            file_path = SAMPLE_AUDIO[selected_audio]
            model = WhisperModel("base", device="cpu")
            segments, _ = model.transcribe(file_path)
            transcript = " ".join([segment.text for segment in segments])
            st.session_state["incident_text"] = transcript
            st.success(f"Transcription from {selected_audio}:")
            st.write(transcript)

    else:
        # Replace this block with the sample-incidents version
        sample_incidents = {
            "Sample 1": "Eng 201 responded to a reported kitchen fire at 1287 Maple Ave. Light smoke was showing from a two-story private home on arrival. Crew advanced a 1¾” hose line into the first-floor kitchen where flames were found on the stovetop and nearby cabinets. Fire was extinguished with water, and cabinets were overhauled to ensure no hidden fire. Ventilation performed by Truck 107. Cause determined to be unattended cooking oil. Smoke alarm activated and warned residents. One adult resident evaluated for smoke inhalation but refused transport. No firefighter injuries.",
            "Sample 2": "Eng 12 and Rescue 2 responded to a four-vehicle accident at Main St and 5th Ave. One male driver was pinned in a sedan. Extrication was performed using the Jaws-of-Life to remove the driver-side door. Patient was stabilized, C-spine precautions taken, and transported by ambulance. Three additional patients transported for evaluation, two refused transport. Smoke was noted from another vehicle, and the battery was disconnected to prevent fire. Traffic rerouted until DOT set up an arrow board.",
            "Sample 3": "Eng 21 responded to a vehicle fire on I-495. On arrival, crew found a sedan with the engine compartment fully involved in flames on the right shoulder. Traffic slowed and a single lane was blocked for safety. Fire extinguished using one 1¾” hose line with foam added to suppress fuel vapors. Battery disconnected after extinguishment. Absorbent applied to leaking motor oil and transmission fluid. Vehicle turned over to tow company after overhaul was completed.",
            "Sample 4": "Eng 8, Truck 33, and Rescue 4 responded to reports of smoke coming from a three-story apartment building at 457 Lincoln Blvd. On arrival, heavy smoke visible from the second-floor windows. Crew advanced a 1¾” hose line to second floor, fire located in bedroom and confined to one unit. Primary and secondary searches negative. Ventilation performed by Truck 33. Utilities secured and fire under control within 20 minutes. Three residents displaced; Red Cross notified. No injuries."
        }

        selected_sample = st.selectbox("Or pick a sample incident:", ["None"] + list(sample_incidents.keys()))

        if selected_sample != "None":
            default_text = sample_incidents[selected_sample]
        else:
            default_text = st.session_state.get("incident_text", "")

        incident_text = st.text_area("Or type/paste the incident description:", value=default_text)
        st.session_state["incident_text"] = incident_text


    if st.button("Parse incident") and st.session_state.get("incident_text", "").strip():
        try:
            response = requests.post(
                "https://operationsmokeybear-dspilots.onrender.com/categorize-transcript",
                json={"transcript": st.session_state["incident_text"]},
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
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Edit fields if needed, then approve before saving")

    st.divider()

    if "parsed" not in st.session_state:
        st.info("No parsed incident yet. Go to 'Record / Input' tab first.")
    else:
        parsed = st.session_state["parsed"]

        # Core fields
        st.subheader("Core Incident Fields")
        parsed_items = [(col, parsed.get(col, "")) for col in COLUMNS]
        # Filled fields first, empty after
        parsed_items.sort(key=lambda x: (x[1] == "" or str(x[1]).strip() == ""))

        for col, value in parsed_items:
            value = st.text_input(
                f"{col}",
                value=value,
                key=f"input_{col}"
            )
            parsed[col] = value

        # Fire fields (auto-appear if fire flagged)
        if str(parsed.get("fire", "")).lower() in ["yes", "true", "1"]:
            st.divider()
            st.subheader("🔥 Fire-Specific Fields")

            fire_items = [(col, parsed.get(col, "")) for col in fire_columns]
            fire_items.sort(key=lambda x: (x[1] == "" or str(x[1]).strip() == ""))

            for col, value in fire_items:
                value = st.text_input(
                    f"{col}",
                    value=value,
                    key=f"input_fire_{col}"
                )
                parsed[col] = value

        # One approval checkbox at the end
        approved = st.checkbox("I approve this form, it is correct")

        if st.button("Save to CSV", disabled=not approved):
            save_incident(parsed)
            st.success("Incident saved to CSV!")
    
        st.markdown("</div>", unsafe_allow_html=True)


with tab3:
    st.subheader("Incident Dashboard")


    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        fire_count = df[df["fire"].astype(str).str.lower().isin(["true", "yes", "1"])].shape[0]
        medical_count = df[df["medical"].astype(str).str.lower().isin(["true", "yes", "1"])].shape[0]
        hazmat_count = df[df["hazsit"].astype(str).str.lower().isin(["true", "yes", "1"])].shape[0]

        col1, col2, col3 = st.columns(3)

        with col1:
            fire_placeholder = st.empty()
            for i in range(fire_count + 1):
                fire_placeholder.markdown(f"<div class='metric-card metric-fire'><h2>🔥 Fires</h2><p>{i}</p></div>", unsafe_allow_html=True)
                time.sleep(0.02)

        with col2:
            medical_placeholder = st.empty()
            for i in range(medical_count + 1):
                medical_placeholder.markdown(f"<div class='metric-card metric-medical'><h2>🚑 Medical</h2><p>{i}</p></div>", unsafe_allow_html=True)
                time.sleep(0.02)

        with col3:
            hazmat_placeholder = st.empty()
            for i in range(hazmat_count + 1):
                hazmat_placeholder.markdown(f"<div class='metric-card metric-hazmat'><h2>☣ Hazmat</h2><p>{i}</p></div>", unsafe_allow_html=True)
                time.sleep(0.02)

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

        # Download combined CSV
        combined_csv = df[COLUMNS + fire_columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Full Dataset",
            data=combined_csv,
            file_name="incidents_master.csv",
            mime="text/csv"
        )
    else:
        st.info("No incidents yet. Add one to see the dashboard.")