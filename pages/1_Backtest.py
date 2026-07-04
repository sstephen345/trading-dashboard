import streamlit as st
import pandas as pd

st.set_page_config(page_title="Backtest", page_icon="📊")

st.title("📊 Backtest")

st.write("Upload your 1-minute Excel file to begin.")

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    st.subheader("Columns")

    st.write(list(df.columns))

    st.subheader("Preview")

    st.dataframe(df.head())