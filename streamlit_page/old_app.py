import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Live Data Dashboard")#, layout="wide")
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
        border-radius: 8px;
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
image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"

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
    FROM hist_10m
    ORDER BY obs_time DESC
    """
df = pd.read_sql_query(query, engine).sort_values('obs_time', ascending=True)


if 'temp' in df.columns:
    df['temp_f'] = (df['temp'] * 9 / 5 + 32).round(1)
    # plot_data = df['temp_f'].reset_index(drop=True)
    idx = df.groupby('sensor_id')['obs_time'].idxmax()
    values = df.loc[idx].reset_index(drop=True)['temp_f'].to_list() + [77.01]
else:
    plot_data = np.random.randn(1000)
    values = np.round(plot_data[-5:], 2)


# --- Plotly Express plot (Seaborn style) ---
legend_order = [
    'PICO_W_01',
    'PICO_W_02',
    'PICO_W_03',
    'PICO_W_04'
]



if {'obs_time', 'temp_f', 'sensor_id'}.issubset(df.columns):
    fig = px.line(
        df,
        x='obs_time',
        y='temp_f',
        color='sensor_id',
        color_discrete_sequence=px.colors.qualitative.D3,
        category_orders={'sensor_id': legend_order},
        labels={
            "obs_time": "Time",
            "temp_f": "Temperature",
            "sensor_id": "Sensor"
        },
        title="Temperature Readings Over Time by Sensor"
    )
    fig.update_layout(
        width=1000,
        height=300,
        legend_title_text='Sensor',
        xaxis_title='Time',
        yaxis_title='Temperature',
        title='Temperature Readings Over Time by Sensor',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
else:
    # fallback: show a random line if data is missing
    plot_data = np.random.randn(1000)
    fig = px.line(y=plot_data, title="Live Data from Database")


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
