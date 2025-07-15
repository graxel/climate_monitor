import os
import streamlit as st
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh


if os.path.basename(os.getcwd()) == "viewer":
    asset_prefix = ""
else:
    asset_prefix = "viewer/"

# =========================
# 2. Get Data
# =========================

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

df = load_data()

# --- Data preprocessing ---
if 'temp' in df.columns:
    df['temp_f'] = (df['temp'] * 9 / 5 + 32)
else:
    df['temp_f'] = np.nan

legend_order = [
    'PICO_W_01',
    'PICO_W_02',
    'PICO_W_03',
    'PICO_W_04'
]

df['obs_time'] = pd.to_datetime(df['obs_time'])
timestamps_dt = [dt.to_pydatetime() for dt in df['obs_time'].sort_values().unique()]


def make_plot(df, selected_time):
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
        # xaxis=dict(
        #     rangeslider=dict(visible=True),
        #     type="date"
        # ),
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
    return fig

# =========================
# 3. Page Layout and UI
# =========================

st.set_page_config(page_title="Live Data Dashboard", layout="wide")
st.title("Live Data Dashboard")

col1, col2 = st.columns(2)

# --- Column 1: Plot and Refresh Button ---
with col1:

    st.subheader("Sensor Temperature History")

    plot_placeholder = st.empty()

    selected_time = st.slider(
        "Select time for overlay",
        min_value=timestamps_dt[0],
        max_value=timestamps_dt[-1],
        value=timestamps_dt[-1],
        step=timedelta(minutes=10),
        format="YYYY-MM-DD HH:mm"
    )

    # Build the plot using the selected_time
    fig = make_plot(df, selected_time)
    plot_placeholder.plotly_chart(fig, use_container_width=True)

# --- Column 2: Overlay Section ---
with col2:

    # CSS for overlaying values on the image
    st.markdown("""
        <style>
        .overlay-container {
            position: relative;
            margin: auto;
        }
        .overlay-image {
            opacity: 0.4;
            width: 100%;
            display: block;
            border-radius: 8px;
        }
        .overlay-label {
            position: absolute;
            color: white;
            font-size: 1em;
            font-weight: bold;
            text-shadow: 2px 2px 4px #000;
        }
        .label1 { bottom: 20%; right: 10%; }
        .label2 { bottom: 35%; right: 30%; }
        .label3 { top: 20%; right: 20%; }
        .label4 { top: 15%; left: 10%; }
        .label5 { bottom: 20%; left: 10%; }
        </style>
    """, unsafe_allow_html=True)

    image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"

    # Find overlay values for selected time
    selected_df = df[df['obs_time'] == pd.Timestamp(selected_time)]
    overlay_values = []
    for sensor in legend_order:
        val = selected_df[selected_df['sensor_id'] == sensor]['temp_f'].round(1)
        overlay_values.append(str(val.values[0]) + "°F" if not val.empty else "N/A")
    while len(overlay_values) < 5:
        overlay_values.append("N/A")

    st.subheader("Data Values for Selected Time")

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
    st.markdown("")
    # Refresh Button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# =========================
# 4. Project Explainer
# =========================

st.markdown("---")  # Horizontal rule for separation

st.header("About This Project")

st.subheader("Overview")
overview_col1, overview_col2 = st.columns([0.5, 0.5])
with overview_col1:
    st.markdown(
    """
    My air conditioner has been acting unpredictably for the past two summers, and
    living in a top-floor loft produces some large temperature gradients in my apartment
    in the summer. I was struggling to maintain a stable temperature in my home, and didn't want
    to run the air conditioner more than I had to, so like any engineer, I knew what I had to do:
    build a complicated system and figure out what exactly was going on.

    As depicted, the system is composed of three major components; sensors,
    a home server, and a web application deployed on Streamlit Cloud. The sensors gather
    temperature and humidity data, send it via MQTT protocol to the server, where an MQTT broker
    receives the data. Another process subscribes to the MQTT channel and inserts the incoming data
    into a Postgres database. Yet another process resamples the raw data to ten minute intervals.
    When the webpage is loaded, the application queries the database for the historical data and
    displays it like you see above. The sections that follow explain each component in detail.
    """)
with overview_col2:
    st.image(asset_prefix+"assets/high-level-diagram-2.jpg", caption="High Level Diagram")


st.subheader("Sensors")
sensors_col1, sensors_col2 = st.columns([0.6, 0.4])
with sensors_col1:
    st.markdown(
    """
    The sensors for this project are based on 
    [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/) microcontrollers.
    These boards use a dual-core Arm Cortex-M0+ processor running up to 133 MHz and include
    integrated 2.4GHz Wi-Fi connectivity, making them a great choice for wireless IoT applications.
    Each device is equipped with two AHT21 temperature and humidity sensors for environmental 
    monitoring. The hardware is assembled using a dead bug soldering style, where components are
    mounted directly to each other in 3D space, rather than on a flat motherboard. This style was
    chosen for its simplicity and elegant layout. The devices are programmed with
    [CircuitPython](https://circuitpython.org), and use the
    [Circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup)
    tool to manage dependencies. Once set up, the Pico W microcontrollers connect to Wi-Fi and send
    sensor data to my home server using the [MQTT protocol](https://mqtt.org).
    """)
    st.image(asset_prefix+"assets/soldered_sensors.jpg", caption="Soldered Final Assembly")

    
with sensors_col2:
    st.image("https://static1.makeuseofimages.com/wordpress/wp-content/uploads/2022/07/Raspberry-Pi-Pico-W.jpg", caption="Raspberry Pi Pico W")

    st.image(asset_prefix+"assets/breadboard.jpg", caption="Breadboard Prototype")

st.subheader("Server")

st.subheader("Webpage")

st.subheader("Analysis")

st.markdown(
    """
    These sections to follow soon!
    """)
#     st.markdown("""
#     - **Raspberry Pi Pico W** microcontrollers used as the core hardware.
#     - Each Pico W is connected to **two AHT21 temperature/humidity sensors**.
#     - Devices programmed with **CircuitPython** for rapid prototyping and easy sensor integration.
#     - Data is sent using the **MQTT protocol** to a central server.
#     - A **PostgreSQL database** stores all incoming sensor data, designed for efficient time-series storage.
#     - Breadboard prototype successfully tested.
#     - Final circuit was designed, soldered, and assembled for real-world deployment.
#     """)
#     st.image(asset_prefix+"assets/breadboard.jpg", caption="Breadboard Prototype")#, use_container_width=True)
#     st.image(asset_prefix+"assets/soldered_sensors.jpg", caption="Soldered Final Assembly", use_container_width=True)

# with exp_col2:
#     st.subheader("Software & Visualization")
#     st.markdown("""
#     - **MQTT server** receives sensor data and writes to the database.
#     - **Database schema** designed for scalable, multi-sensor time series data.
#     - Used `circup` and `poetry` for CircuitPython and Python dependency management.
#     - This dashboard built with **Streamlit** for live data visualization and interaction.
#     - Interactive plots show real-time and historical sensor readings.
#     - Overlay feature displays current values directly on a floorplan image.
#     """)
#     st.image("https://static1.makeuseofimages.com/wordpress/wp-content/uploads/2022/07/Raspberry-Pi-Pico-W.jpg", caption="Pico W with Sensors", use_container_width=True)
