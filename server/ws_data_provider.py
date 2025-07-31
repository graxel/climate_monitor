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
}

def query_db():
    with engine.connect() as conn:
        # Grab most recent observation per sensor_id
        query = """
            SELECT DISTINCT ON (sensor_id) sensor_id, obs_time, temp1, hum1, temp2, hum2
            FROM observations
            ORDER BY sensor_id, obs_time DESC
        """
        df = pd.read_sql_query(text(query), conn)

    if df.empty:
        return {}

    df['temp'] = (df['temp1'] + df['temp2']) / 2
    df['hum'] = (df['hum1'] + df['hum2']) / 2
    df['sensor_loc'] = df['sensor_id'].map(SENSOR_MAPPING)

    temp_hum = {}
    for _, row in df.iterrows():
        loc = row['sensor_loc']
        if loc:
            temp_c = row['temp']
            hum = row['hum']
            temp_f = temp_c * 9 / 5 + 32
            temp_hum[loc] = {'temp': round(temp_f, 2), 'hum': round(hum, 2)}

    return temp_hum

async def get_data():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sensor_data = await asyncio.to_thread(query_db)

    data = {
        "timestamp": now_str,
        "sensor_data": {
            "office_temp": sensor_data['office']['temp'] or 72,
            "office_hum": sensor_data['office']['hum'] or 45,
            "kitchen_temp": sensor_data['kitchen']['temp'] or 74,
            "kitchen_hum": sensor_data['kitchen']['hum'] or 50,
            "closet_temp": sensor_data['closet']['temp'] or 75,
            "closet_hum": sensor_data['closet']['hum'] or 48,
            "bedroom_temp": sensor_data['bedroom']['temp'] or 73,
            "bedroom_hum": sensor_data['bedroom']['hum'] or 51,
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
        }
    }
    return data

if __name__ == "__main__":
    result = asyncio.run(get_data())
    print(result)