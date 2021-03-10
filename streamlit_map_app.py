import streamlit as st
import pandas as pd
import numpy as np

st.title("Toronto Crime Analysis")

crime_df = pd.read_csv("./data/processed/crime_data.csv").rename(columns={"long": "lon"})

st.map(crime_df[["lat", "lon"]])