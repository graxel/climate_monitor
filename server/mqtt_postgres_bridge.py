import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
import paho.mqtt.client as mqtt


# Load environment variables from .env file
load_dotenv()

# Access variables using os.getenv
PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))  # Cast to int if needed
MQTT_TOPIC = os.getenv("MQTT_TOPIC")


# Connect to PostgreSQL
conn = psycopg2.connect(
    host=PG_HOST,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD
)
cur = conn.cursor()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        # Expecting CSV: sensor_id,timestamp,temp1,hum1,temp2,hum2
        payload = msg.payload.decode()
        parts = payload.strip().split(',')
        sensor_id = parts[0]
        obs_time = datetime.fromtimestamp(float(parts[1]))
        temp1 = float(parts[2])
        hum1 = float(parts[3])
        temp2 = float(parts[4])
        hum2 = float(parts[5])

        # Insert into PostgreSQL
        cur.execute(
            """
            INSERT INTO observations (sensor_id, obs_time, temp1, hum1, temp2, hum2)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (sensor_id, obs_time, temp1, hum1, temp2, hum2)
        )
        conn.commit()
        print(f"Inserted data from {sensor_id} at {obs_time}")
    except Exception as e:
        print("Error processing message:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
