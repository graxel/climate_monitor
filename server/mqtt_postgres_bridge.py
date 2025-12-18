import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
import paho.mqtt.client as mqtt

load_dotenv()

required_vars = ["PG_HOST", "PG_DB", "PG_USER", "PG_PASSWORD", "PG_WRITE_USER", "PG_WRITE_PASSWORD", "MQTT_BROKER", "MQTT_PORT", "MQTT_TOPIC"]

missing = [var for var in required_vars if var not in os.environ]
if missing:
    print(f"Missing environment variables: {', '.join(missing)}")
    sys.exit(1)

PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_WRITE_USER")
PG_PASSWORD = os.getenv("PG_WRITE_PASSWORD")
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))  # Cast to int if needed
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == mqtt.CONNACK_ACCEPTED:
        print("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with reason code {reason_code}")

def on_message(client, userdata, msg):
    try:
        # Expecting CSV: sensor_id,timestamp,temp1,hum1,temp2,hum2
        payload = msg.payload.decode()
        parts = payload.strip().split(',')
        if len(parts) != 6:
            print(f"Malformed payload ({payload}); expected 6 fields.")
            sys.exit(1)
        sensor_id = parts[0]
        obs_time = datetime.fromtimestamp(float(parts[1]))
        temp1 = float(parts[2])
        hum1 = float(parts[3])
        temp2 = float(parts[4])
        hum2 = float(parts[5])

        with psycopg2.connect(
            host=PG_HOST,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO observations (sensor_id, obs_time, temp1, hum1, temp2, hum2)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (sensor_id, obs_time, temp1, hum1, temp2, hum2)
                )
                cur.execute(
                    """
                    INSERT INTO update_status (table_name, sensor_id, last_updated)
                    VALUES ('observations', %s, %s)
                    ON CONFLICT (table_name, sensor_id)
                    DO UPDATE SET last_updated = EXCLUDED.last_updated
                    WHERE update_status.last_updated < EXCLUDED.last_updated
                    """,
                    (sensor_id, obs_time)
                )
                conn.commit()
        print(f"Inserted data from {sensor_id} at {obs_time}")
    except Exception as e:
        print(f"Error processing message: {msg}")
        print(e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
