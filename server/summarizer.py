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
    result = conn.execute(text("SELECT MAX(obs_time) FROM webpage_plot_data"))
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
    df['temp_diff'] = df['temp1'] - df['temp2']
    df['hum_diff'] = df['hum1'] - df['hum2']

    df['temp_f'] = df['temp'] * 9 / 5 + 32

    sensor_mapping = {
        'PICO_W_01': 'office',
        'PICO_W_02': 'kitchen',
        'PICO_W_03': 'closet',
        'PICO_W_04': 'bedroom',
    }
    df['sensor_loc'] = df['sensor_id'].map(sensor_mapping)

    # 3. Group by sensor_id and 5-min interval, average temp1 and hum1
    df['interval_time'] = pd.to_datetime(df['obs_time']).dt.round('5min')
    agg = (
        df.groupby(['interval_time', 'sensor_loc'],)
            .agg(temp=('temp_f', 'mean'), hum=('hum', 'mean'))
            .reset_index()
            .rename(columns={'interval_time': 'obs_time'})
    )

    # leave off incomplete data at end
    hist_5m = agg[agg['obs_time'] < agg['obs_time'].max()]

    # from long format to wide
    wide = hist_5m.pivot(
        index='obs_time',
        columns='sensor_loc',
        values=['temp', 'hum']
    ).swaplevel(axis=1).sort_index(axis=1).reset_index()

    def flatten_col(col_tuple):
        prefix = '' if col_tuple[0] == 'obs_time' else 'sensor__'

        # Drop empty strings and join with underscores
        return prefix + '_'.join([str(x) for x in col_tuple if x])

    # flatten cols from multiindex to regular
    wide.columns = [flatten_col(col) for col in wide.columns]

    # 4. Delete overlapping intervals in webpage_plot_data and insert new aggregates
    with engine.begin() as conn:
        min_interval = wide['obs_time'].min()
        conn.execute(
            text("""
                DELETE FROM webpage_plot_data
                WHERE obs_time >= :min_interval
            """),
            {"min_interval": min_interval}
        )
        wide.to_sql('webpage_plot_data', conn, if_exists='append', index=False)
