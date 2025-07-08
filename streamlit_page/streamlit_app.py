import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh

# --- Auto-refresh every 3 seconds (3000 ms) ---
st_autorefresh(interval=3000, key="live_data_autorefresh")  # [2][5]

st.set_page_config(page_title="Live Data Dashboard", layout="wide")
st.title("Live Data Dashboard")

# --- CSS for overlaying values on the image ---
st.markdown("""
    <style>
    .overlay-container {
        position: relative;
        width: 600px;
        margin: auto;
    }
    .overlay-image {
        width: 100%;
        display: block;
        border-radius: 12px;
    }
    .overlay-label {
        position: absolute;
        color: white;
        font-size: 1.5em;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
    }
    .label1 { top: 10%; left: 10%; }
    .label2 { top: 10%; right: 10%; }
    .label3 { top: 50%; left: 45%; }
    .label4 { bottom: 10%; left: 10%; }
    .label5 { bottom: 10%; right: 10%; }
    </style>
""", unsafe_allow_html=True)

# --- Image for overlay ---
image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"  # [1]

# --- Database connection ---
DB_HOST = st.secrets['DB_HOST']
DB_PORT = st.secrets['DB_PORT']
DB_NAME = st.secrets['DB_NAME']
DB_USER = st.secrets['DB_USER']
DB_PASSWORD = st.secrets['DB_PASSWORD']

db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

query = """
    SELECT *
    FROM observations
    """
df = pd.read_sql_query(query, engine)

# --- Visualization logic ---
points = 20  # Number of points to show in the chart

if 'temp1' in df.columns:
    plot_data = df['temp1'].tail(points).reset_index(drop=True)
else:
    plot_data = np.random.randn(points)

fig = px.line(y=plot_data, title="Live Data from Database")

# Use 5 latest values for overlay, or random if not enough data
if 'temp1' in df.columns and len(df) >= 5:
    values = df['temp1'].head(5).values
else:
    values = np.round(np.random.uniform(0, 100, 5), 2)

placeholder = st.empty()
with placeholder.container():
    st.subheader("Interactive Plot (Live from Database)")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Live Data Values (Superimposed)")
    st.markdown(f"""
    <div class="overlay-container">
        <img src="{image_url}" class="overlay-image"/>
        <div class="overlay-label label1">Value 1: {values[0]}</div>
        <div class="overlay-label label2">Value 2: {values[1]}</div>
        <div class="overlay-label label3">Value 3: {values[2]}</div>
        <div class="overlay-label label4">Value 4: {values[3]}</div>
        <div class="overlay-label label5">Value 5: {values[4]}</div>
    </div>
    """, unsafe_allow_html=True)
