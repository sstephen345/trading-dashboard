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
target_to = st.number_input("Target To", value=100, step=10)
target_step = st.number_input("Target Step", value=10, step=10)
st.subheader("📈 Filter Ranges")

use_ema = st.checkbox("Optimize EMA Filter", value=True)
ema_values = [0.0, 0.5, 1.0, 1.5] if use_ema else [0.0]

use_atr = st.checkbox("Optimize ATR Filter", value=False)
atr_values = [0.0, 0.1, 0.2, 0.5] if use_atr else [0.0]

use_gamma = st.checkbox("Optimize Gamma Filter", value=False)
gamma_values = [0.0, 0.5, 1.0] if use_gamma else [0.0]

use_rsi = st.checkbox("Optimize RSI Filter", value=False)
rsi_ranges = [(40, 70), (45, 70), (50, 70), (40, 65)] if use_rsi else [(0, 100)]

ranking_method = st.selectbox(
    "Rank Results By",
    ["Profit Factor", "Net Points", "Win Rate %", "Lowest Drawdown"]
)

if st.button("🚀 Run Auto Optimization"):
    st.write("Optimizer button is working.")