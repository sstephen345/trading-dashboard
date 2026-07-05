import streamlit as st
import pandas as pd
from strategy.flexible_engine import run_flexible_strategy

st.set_page_config(page_title="Auto Optimizer", page_icon="🧠")

st.title("🧠 Auto Optimizer")
st.write("Automatically test multiple strategy combinations.")

if "df" not in st.session_state:
    st.warning("Please upload Excel from Dashboard first.")
    st.stop()

df = st.session_state["df"]

st.success("✅ Dataset loaded from Dashboard")

st.subheader("📌 Trade Direction")

direction = st.selectbox(
    "Select Direction",
    ["Both CE and PE", "CE Only", "PE Only"]
)

allow_ce = direction in ["Both CE and PE", "CE Only"]
allow_pe = direction in ["Both CE and PE", "PE Only"]

st.subheader("⚙️ SL / Target Range")

sl_from = st.number_input("SL From", value=10, step=5)
sl_to = st.number_input("SL To", value=50, step=5)
sl_step = st.number_input("SL Step", value=5, step=5)

target_from = st.number_input("Target From", value=20, step=10)
target_to = st.number