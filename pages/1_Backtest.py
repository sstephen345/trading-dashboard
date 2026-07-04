import streamlit as st
import pandas as pd

st.set_page_config(page_title="Backtest", page_icon="📊")

st.title("📊 Backtest")
st.write("Upload your 1-minute Excel file to validate the data.")

REQUIRED_COLUMNS = [
    "date",
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

    columns_lower = [str(c).strip().lower() for c in df.columns]

    st.subheader("📋 Data Summary")

    col1, col2 = st.columns(2)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))

    st.subheader("✅ Data Health Check")

    missing_cols = []
    for required in REQUIRED_COLUMNS:
        if required.lower() not in columns_lower:
            missing_cols.append(required)

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

    st.subheader("📅 Date & Time Handling")

    if "date" in columns_lower:
        date_col = df.columns[columns_lower.index("date")]

        try:
            datetime_values = pd.to_datetime(df[date_col])

            df["Date_Only"] = datetime_values.dt.date
            df["Time_Only"] = datetime_values.dt.time

            st.success("✅ Date/Time column detected successfully.")
            st.info("ℹ️ Separate Date and Time fields created automatically.")

            st.write(f"Start Date: **{datetime_values.min().date()}**")
            st.write(f"End Date: **{datetime_values.max().date()}**")
            st.write(f"Trading Days: **{datetime_values.dt.date.nunique()}**")

            st.write(f"Start Time: **{datetime_values.min().time()}**")
            st.write(f"End Time: **{datetime_values.max().time()}**")

        except Exception as e:
            st.error("❌ Could not read the Date column as datetime.")
            st.write(str(e))
    else:
        st.error("❌ Date column not found.")

    st.subheader("📌 Columns Found")
    st.write(list(df.columns))

    st.subheader("👀 Preview")
    st.dataframe(df.head())