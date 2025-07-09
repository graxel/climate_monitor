import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()

PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB = os.getenv('PG_DB')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')

db_url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(db_url)

# 1. Find latest aggregated interval
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(obs_time) FROM hist_10m"))
    latest_history = result.scalar()

# 2. Query new data from raw table
lower_bound = latest_history if latest_history else '1970-01-01'

query = f"""
    SELECT sensor_id, obs_time, temp1, hum1, temp2, hum2
    FROM observations
    WHERE obs_time > '{lower_bound}'
"""
df = pd.read_sql_query(query, engine)

if not df.empty:

    df['temp'] = (df['temp1'] + df['temp2']) / 2
    df['hum'] = (df['hum1'] + df['hum2']) / 2

    # 3. Group by sensor_id and 10-min interval, average temp1 and hum1
    df['interval_start'] = pd.to_datetime(df['obs_time']).dt.floor('10min')
    agg = (
        df.groupby(['interval_start', 'sensor_id'],)
            .agg(temp=('temp', 'mean'), hum=('hum', 'mean'))
            .reset_index()
            .rename(columns={'interval_start': 'obs_time'})
    )
    hist_10m = agg[agg['obs_time'] < agg['obs_time'].max()]

    # 4. Delete overlapping intervals in hist_10m and insert new aggregates
    with engine.begin() as conn:
        min_interval = agg['obs_time'].min()
        conn.execute(
            text("""
                DELETE FROM hist_10m
                WHERE obs_time >= :min_interval
            """),
            {"min_interval": min_interval}
        )
        hist_10m.to_sql('hist_10m', conn, if_exists='append', index=False)
