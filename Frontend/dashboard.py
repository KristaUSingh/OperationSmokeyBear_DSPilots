import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from faster_whisper import WhisperModel
import requests
import tempfile
import os

st.set_page_config(page_title="Operation Smokey Bear", page_icon="🧑‍🚒", layout="wide")

# ===== CSS THEME =====
st.markdown("""
<style>
/* ===== BACKGROUND ===== */
html, body, .stApp {
    background: radial-gradient(circle at top left, rgba(255,107,53,0.08), transparent 70%),
                radial-gradient(circle at bottom right, rgba(79,142,247,0.08), transparent 70%),
                #0E1117;
    font-family: 'Inter', sans-serif;
}

/* ===== TITLE ===== */
h1 {
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
    font-size: 2.8rem;
    letter-spacing: 2px;
    text-shadow: 0 0 25px #FF6B35, 0 0 50px rgba(255,107,53,0.7);
    margin-bottom: 0.8rem;
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
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.title("WELCOME TO OPERATION SMOKEY BEAR 🔥🧸!")
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
fire_columns = pd.read_csv("mod_fire.csv")["name"].dropna().tolist()

COLUMNS = [
  "incident_neris_id","incident_internal_id","incident_final_type","incident_final_type_primary",
  "incident_special_modifier","fire","medical","hazsit","emerging_hazard","tactic_timestamps",
  "incident_point","incident_polygon","incident_location","incident_location_use","incident_people_present",
  "incident_displaced_number","incident_displaced_cause","exposure","rescue_ff","rescue_nonff",
  "incident_rescue_animal","incident_actions_taken","incident_noaction","unit_response","risk_reduction",
  "incident_aid_direction","incident_aid_type","incident_aid_department_name","incident_aid_nonfd",
  "incident_narrative_impediment","incident_narrative_outcome","parcel","weather"
]
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
    st.markdown("### 🎤 Tap to Start Recording", unsafe_allow_html=True)

    # 🎤 Mic Button Wrapper
    st.markdown("<div class='mic-btn-wrapper'><div class='mic-btn' id='mic-button'>", unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="▶️ Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

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
        st.success("Audio transcribed successfully (faster-whisper)!")

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
                value = parsed.get(col) if col in parsed else ""
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
    
        st.markdown("</div>", unsafe_allow_html=True)


with tab3:
    st.subheader("Incident Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card metric-fire'><h3>🔥 Fires</h3><p>12</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card metric-medical'><h3>🚑 Medical</h3><p>7</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card metric-hazmat'><h3>☣ Hazmat</h3><p>2</p></div>", unsafe_allow_html=True)


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

        # Download combined CSV
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