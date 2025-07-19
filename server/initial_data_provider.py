from flask import Flask, jsonify
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

app = Flask(__name__)

def get_db_connection():
    db_url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(db_url)
    return engine
    
@app.route("/api/initial_data")
def initial_data():

    engine = get_db_connection()

    query = """
        SELECT *
        FROM webpage_plot_data
        WHERE obs_time >= CURRENT_DATE - INTERVAL '2 days'
        """

    df = pd.read_sql_query(query, engine).sort_values('obs_time', ascending=True)


    data_types = {
        'sensor_data': 'sensor__',
        'home_data': 'home__',
        'weather_data': 'weather__'
    }

    d = {'obs_time': df['obs_time'].head().to_list()}
    for data_type_key, data_type_value in data_types.items():
        for col in df.columns:
            if col.startswith(data_type_value):
                col_end = col.partition('__')[2]
                data = df[col].head().to_list()
                if data_type_key in d:
                    d[data_type_key][col_end] = data
                else:
                    d[data_type_key] = {col_end: data}
    return jsonify(d)

if __name__ == "__main__":
    app.run(debug=True)
