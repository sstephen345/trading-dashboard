import streamlit as st
import pandas as pd

st.set_page_config(page_title="Backtest", page_icon="📊")

st.title("📊 Backtest")
st.write("Upload your 1-minute Excel file to validate the data.")

REQUIRED_COLUMNS = [
    "date",
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "EMA20",
    "EMA_Slope",
    "ATR14",
    "ATR_Slope",
    "Gamma_Momentum",
]

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    st.subheader("📋 Data Summary")

    col1, col2 = st.columns(2)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))

    st.subheader("✅ Data Health Check")

    columns_lower = [str(c).strip().lower() for c in df.columns]
    required_lower = [c.lower() for c in REQUIRED_COLUMNS]

    missing_cols = [
        REQUIRED_COLUMNS[i]
        for i, col in enumerate(required_lower)
        if col not in columns_lower
    ]

    if len(missing_cols) == 0:
        st.success("✅ Required columns: OK")
    else:
        st.error("❌ Missing required columns:")
        st.write(missing_cols)

    missing_values = df.isna().sum().sum()

    if missing_values == 0:
        st.success("✅ Missing values: 0")
    else:
        st.warning(f"⚠️ Missing values found: {missing_values}")

    st.subheader("📅 Date Range")

    if "date" in columns_lower:
        date_col = df.columns[columns_lower.index("date")]
        try:
            dates = pd.to_datetime(df[date_col])
            st.write(f"Start Date: **{dates.min().date()}**")
            st.write(f"End Date: **{dates.max().date()}**")
            st.write(f"Trading Days: **{dates.dt.date.nunique()}**")
        except Exception:
            st.warning("Could not read date column properly.")
    else:
        st.warning("Date column not found.")

    st.subheader("📌 Columns Found")
    st.write(list(df.columns))

    st.subheader("👀 Preview")
    st.dataframe(df.head())