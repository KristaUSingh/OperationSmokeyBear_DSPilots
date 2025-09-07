import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os

st.set_page_config(page_title="Operation Smokey Bear", page_icon="🧑‍🚒", layout="wide")

# App Title 
st.title("🧑‍🚒 WELCOME TO OPERATION SMOKEY BEAR!")

# Master CSV setup
CSV_FILE = "incidents_master.csv"
COLUMNS = ["incident_id", "timestamp", "type", "address", "injuries", "narrative"]

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

def save_incident(data):
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Tabs
tab1, tab2, tab3 = st.tabs(["🎙️ Record / Input", "🧾 Review & Save", "📊 Dashboard"])

# Tab 1: Record / Input
with tab1:
    st.header("Please click 'Record' or paste text below to log an incident")
    st.subheader("Record or enter incident details")

    # Button placeholder
    st.button("Start recording")  # you can wire in microphone or upload later

    # Free text box
    incident_text = st.text_area("Or type/paste the incident description:")

    if st.button("Parse incident"):
        # Basic parsing placeholder
        parsed = {
            "incident_id": f"INC-{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Structure Fire" if "fire" in incident_text.lower() else "Unknown",
            "address": "123 Main St" if "main" in incident_text.lower() else "",
            "injuries": "0",
            "narrative": incident_text,
        }
        st.session_state["parsed"] = parsed
        st.success("Incident parsed! Check the Review tab.")

# Tab 2: Review & Save 
with tab2:
    st.header("Please review your transcription below and form details")
    st.subheader("Review extracted data")

    if "parsed" not in st.session_state:
        st.info("No parsed incident yet. Go to 'Record / Input' tab first.")
    else:
        parsed = st.session_state["parsed"]
        st.write(parsed)

        if st.button("Save to CSV"):
            save_incident(parsed)
            st.success("Incident saved to CSV!")

# Tab 3: Dashboard 
with tab3:
    st.subheader("Incident Dashboard")

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        st.info("No incidents yet. Add one to see the dashboard.")
    else:
        st.dataframe(df)
        st.bar_chart(df["type"].value_counts())
