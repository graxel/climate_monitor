import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Query your table
query = "SELECT obs_time, temp1, temp2 FROM observations;"
df = pd.read_sql(query, conn)
conn.close()

df['obs_time'] = pd.to_datetime(df['obs_time'], utc=True)#.dt.tz_convert('US/Eastern')

# Plot
plt.figure(figsize=(8, 5))
plt.plot(df['obs_time'], df['temp1'], marker='o', label='temp1')
plt.plot(df['obs_time'], df['temp2'], marker='o', label='temp2')
plt.xlabel('obs_time')
plt.ylabel('temps')
plt.title('temps vs obs_time')
plt.grid(True)
plt.show()
