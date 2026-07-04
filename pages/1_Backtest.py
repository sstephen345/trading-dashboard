import streamlit as st
import pandas as pd

st.title("📊 Backtest")

uploaded_file = st.file_uploader(
    "Upload 1-minute Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully!")

    st.write(f"Rows : {len(df)}")
    st.write(f"Columns : {len(df.columns)}")

    st.subheader("Preview")

    st.dataframe(df.head())