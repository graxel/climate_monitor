import streamlit as st
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh

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
        border-radius: 8px;
    }
    .overlay-label {
        position: absolute;
        color: white;
        font-size: 1.5em;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
    }
    .label1 { bottom: 10%; right: 10%; }
    .label2 { top: 10%; right: 10%; }
    .label3 { top: 50%; left: 45%; }
    .label4 { bottom: 10%; left: 10%; }
    .label5 { top: 10%; left: 10%; }
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

@st.cache_data
def load_data():
    return pd.read_sql_query(query, engine).sort_values('obs_time', ascending=True)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

df = load_data()


if 'temp' in df.columns:
    df['temp_f'] = (df['temp'] * 9 / 5 + 32).round(1)
else:
    df['temp_f'] = np.nan

legend_order = [
    'PICO_W_01',
    'PICO_W_02',
    'PICO_W_03',
    'PICO_W_04'
]

# --- Ensure obs_time is datetime and create list of Python datetimes for slider ---
df['obs_time'] = pd.to_datetime(df['obs_time'])
timestamps_dt = [dt.to_pydatetime() for dt in df['obs_time'].sort_values().unique()]

# --- Layout: Plot and slider in col1, overlay in col2 ---
# --- Layout: Plot and slider in col1, overlay in col2 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Interactive Plot (Live from Database)")

    # 1. Show the plotly chart placeholder (will fill it after the slider)
    plot_placeholder = st.empty()

    # 2. Show the slider (this will appear above the plot in code, but we will fill the plot placeholder after)
    selected_time = st.slider(
        "Select time for overlay",
        min_value=timestamps_dt[0],
        max_value=timestamps_dt[-1],
        value=timestamps_dt[-1],
        step=timedelta(minutes=10),
        format="YYYY-MM-DD HH:mm"
    )

    # 3. Build the plot using the selected_time
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
        }
    )
    fig.update_layout(
        legend_title_text='Sensor',
        xaxis_title='Time',
        yaxis_title='Temperature',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        ),
    )
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    # Add red dot indicators for each sensor at the selected time
    for sensor in legend_order:
        y_val = df[
            (df['sensor_id'] == sensor) &
            (df['obs_time'] == pd.Timestamp(selected_time))
        ]['temp_f']
        if not y_val.empty:
            fig.add_trace(
                go.Scatter(
                    x=[selected_time],
                    y=[y_val.values[0]],
                    mode="markers",
                    marker=dict(color="red", size=12, symbol="circle"),
                    name=f"{sensor} selected",
                    showlegend=False
                )
            )

    # 4. Fill the plot placeholder (so the plot appears below the slider)
    plot_placeholder.plotly_chart(fig, use_container_width=True)


with col2:
    # Find overlay values for selected time
    selected_df = df[df['obs_time'] == pd.Timestamp(selected_time)]
    overlay_values = []
    for sensor in legend_order:
        val = selected_df[selected_df['sensor_id'] == sensor]['temp_f']
        overlay_values.append(val.values[0] if not val.empty else "N/A")
    while len(overlay_values) < 5:
        overlay_values.append("N/A")

    st.subheader("Live Data Values (Superimposed)")
    st.markdown(f"""
    <div class="overlay-container">
        <img src="{image_url}" class="overlay-image"/>
        <div class="overlay-label label1">Office: {overlay_values[0]}</div>
        <div class="overlay-label label2">Kitchen: {overlay_values[1]}</div>
        <div class="overlay-label label3">Closet: {overlay_values[2]}</div>
        <div class="overlay-label label4">Bedroom: {overlay_values[3]}</div>
        <div class="overlay-label label5">other: {overlay_values[4]}</div>
    </div>
    """, unsafe_allow_html=True)
