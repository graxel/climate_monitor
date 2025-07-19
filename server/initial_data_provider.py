from flask import Flask, jsonify
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd


# Load environment variables from .env file
load_dotenv()

# Access variables using os.getenv
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

app = Flask(__name__)

db_url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(db_url)

query = """
    SELECT *
    FROM hist_10m
    WHERE obs_time >= CURRENT_DATE - INTERVAL '2 days'
    ORDER BY obs_time DESC
    """

def load_data():
    return pd.read_sql_query(query, engine).sort_values('obs_time', ascending=True)

df = load_data()

    # Format as list of dicts
    result = [
        {'timestamp': str(row[0]), 'office_temp': row[1]}
        for row in rows
    ]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
