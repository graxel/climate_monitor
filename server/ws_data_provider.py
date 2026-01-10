import random
import asyncio
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text

from postgres_auth import db_url


engine = create_engine(db_url, pool_pre_ping=True)

SENSOR_MAPPING = {
    'PICO_W_01': 'office',
    'PICO_W_02': 'kitchen',
    'PICO_W_03': 'closet',
    'PICO_W_04': 'bedroom',
    'PICO_W_05': 'couch',
    'PICO_W_06': 'vent',
    'PICO_W_07': 'thermostat',
}

def query_observations():
    with engine.connect() as conn:
        # Grab most recent observation per sensor_id
        query = """
            SELECT DISTINCT ON (sensor_id) sensor_id, obs_time, temp1, hum1, temp2, hum2, co2, aqi
            FROM observations
            ORDER BY sensor_id, obs_time DESC
        """
        df = pd.read_sql_query(text(query), conn)

    if df.empty:
        return {}

    df['temp'] = df['temp1'] # (df['temp1'] + df['temp2']) / 2   # need to do this on a sensor by sensor basis
    df['hum'] = df['hum1'] # (df['hum1'] + df['hum2']) / 2
    df['sensor_loc'] = df['sensor_id'].map(SENSOR_MAPPING)

    temp_hum = {}
    for _, row in df.iterrows():
        loc = row['sensor_loc']
        if loc:
            temp_c = row['temp']
            hum = row['hum']
            co2 = row['co2']
            aqi = row['aqi']
            temp_f = temp_c * 9 / 5 + 32
            temp_hum[loc] = {
                'temp': round(temp_f, 2),
                'hum': round(hum, 2),
                'co2': co2,
                'aqi': aqi
            }

    return temp_hum


def query_updates():
    with engine.connect() as conn:
        # Grab most recent update times
        sensor_ids = ", ".join(f"'{s}'" for s in SENSOR_MAPPING.keys())
        query = f"""
            SELECT *
            FROM update_status
            WHERE sensor_id IN ({sensor_ids})
            ORDER BY table_name ASC, sensor_id ASC
        """

        df = pd.read_sql_query(text(query), conn)

    if df.empty:
        return {}

    update_times = {}

    # Group rows by 'table_name'
    grouped = df.groupby("table_name")

    for table_name, group in grouped:
        # Create a dict of sensor_id -> last_updated for each group
        updates = dict(zip(group["sensor_id"], group["last_updated"].astype(str)))
        update_times[table_name] = updates

    return update_times


async def get_data():
    now_str = datetime.now().isoformat()

    sensor_data = await asyncio.to_thread(query_observations)
    update_times = await asyncio.to_thread(query_updates)

    data = {
        "timestamp": now_str,
        "sensor_data": {
            "office_temp": sensor_data['office']['temp'] or 72,
            "office_hum": sensor_data['office']['hum'] or 45,
            "office_co2": sensor_data['office']['co2'] or 400,
            "office_aqi": sensor_data['office']['aqi'] or 0,

            "kitchen_temp": sensor_data['kitchen']['temp'] or 74,
            "kitchen_hum": sensor_data['kitchen']['hum'] or 50,

            "closet_temp": sensor_data['closet']['temp'] or 75,
            "closet_hum": sensor_data['closet']['hum'] or 48,

            "bedroom_temp": sensor_data['bedroom']['temp'] or 73,
            "bedroom_hum": sensor_data['bedroom']['hum'] or 51,
            "bedroom_co2": sensor_data['bedroom']['co2'] or 400,
            "bedroom_aqi": sensor_data['bedroom']['aqi'] or 0,

            "couch_temp": sensor_data['couch']['temp'] or 72,
            "couch_hum": sensor_data['couch']['hum'] or 45,
            "couch_co2": sensor_data['couch']['co2'] or 400,
            "couch_aqi": sensor_data['couch']['aqi'] or 0,

            "thermostat_temp": sensor_data['thermostat']['temp'] or 74,
            "thermostat_hum": sensor_data['thermostat']['hum'] or 50,

            "vent_temp": sensor_data['vent']['temp'] or 75,
            "vent_hum": sensor_data['vent']['hum'] or 48,
        },
        "home_data": {
            "ac_on": 0,
            "windows_open": 0,
            "door_open": 0
        },
        "weather_data": {
            "sun_direction": 114,
            "sun_altitude": 20,
            "cloud_cover": 30,
            "temperature": 87,
            "humidity": 67
        },
        "update_times": update_times
    }
    return data

if __name__ == "__main__":
    result = asyncio.run(get_data())
    print(result)