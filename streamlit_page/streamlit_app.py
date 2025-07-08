import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import psycopg2

st.set_page_config(page_title="Live Data Dashboard", layout="wide")
st.title("Live Data Dashboard")

# --- Database connection ---
@st.cache_resource(show_spinner=False)
def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]
    )

def fetch_live_data():
    conn = get_connection()
    query = "SELECT * FROM observations ORDER BY obs_time DESC LIMIT 100;"  # Modify as needed
    df = pd.read_sql(query, conn)
    return df

# --- Controls for the interactive plot ---
points = st.slider("Number of data points", 10, 100, 50)

# --- Placeholder for live updates ---
placeholder = st.empty()

# --- Image for overlay ---
image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"

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

# --- Main live update loop ---
for u in range(200):
    # --- Query the database for live data ---
    df = fetch_live_data()
    # For demo, use the last 'points' rows and a column called 'value'
    plot_data = df['temp1'].tail(points).reset_index(drop=True) if 'temp1' in df.columns else np.random.randn(points)
    fig = px.line(y=plot_data, title="Live Data from Database")

    # Use 5 latest values for overlay, or random if not enough data
    if len(df) >= 5:
        values = df['temp1'].head(5).values
    else:
        values = np.round(np.random.uniform(0, 100, 5), 2)

    with placeholder.container():
        st.subheader("Interactive Plot (Live from Database)")
        st.plotly_chart(fig, use_container_width=True, key=f"live_plot_{u}")

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
    time.sleep(10)
