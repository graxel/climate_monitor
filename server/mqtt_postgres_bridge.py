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
MQTT_PORT = int(os.getenv("MQTT_PORT"))  # Cast to int
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

FORMAT_REF = {
    't': ['temp1', 'temp2'],
    'h': ['hum1', 'hum2'],
    'c': ['co2'],
    'a': ['aqi'],
    'w': ['window_open'],
    'd': ['door_open'],
}

DATA_TYPES = {
    't': float,
    'h': float,
    'c': float,
    'a': float,
    'w': int,
    'd': int,
}

def parse_sensor_data(format_spec, parts):

    sensor_values = {}
    letter_counts = {letter: 0 for letter in FORMAT_REF}
    
    for i, letter in enumerate(format_spec):
        if letter in FORMAT_REF:
            letter_counts[letter] += 1
            col_list = FORMAT_REF[letter]
            data_type = DATA_TYPES[letter] # typecasting function
            
            if letter_counts[letter] <= len(col_list):
                col_name = col_list[letter_counts[letter] - 1]
                try:
                    sensor_values[col_name] = data_type(parts[3 + i])
                except (ValueError, IndexError):
                    pass
        else:
            print(f"Format spec letter '{letter}' not recognized.")
    
    return sensor_values



def build_insert_query(sensor_id, obs_time, sensor_values):
    column_names = ['sensor_id', 'obs_time']
    values = [sensor_id, obs_time]
    
    for col_name in sensor_values:
        column_names.append(col_name)
        values.append(sensor_values[col_name])
    
    columns_str = ', '.join(column_names)
    placeholders = ', '.join(['%s'] * len(column_names))
    query_with_placeholders = f"INSERT INTO observations ({columns_str}) VALUES ({placeholders})"
    
    return query_with_placeholders, values


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

        if len(parts) < 3:
            print(f"Malformed payload (too few fields): {payload}")
            return
        
        ################################################
        # temporary backwards compatibility vv

        # If first field is NOT a format spec, assume old format
        is_old_format = not all(c in 'thcawd' for c in parts[0].lower())
        
        if is_old_format:
            # Old format: sensor_id,timestamp,temp1,hum1,temp2,hum2
            if len(parts) != 6:
                print(f"Old format payload must have exactly 6 fields: {payload}")
                return
            
            sensor_id = parts[0]
            obs_time = datetime.fromtimestamp(float(parts[1]))
            sensor_values = {
                'temp1': float(parts[2]),
                'hum1': float(parts[3]),
                'temp2': float(parts[4]),
                'hum2': float(parts[5]),
            }
        else:

        # temporary backwards compatibility ^^
        #################################################
        # temporarily indented

            format_spec = parts[0]
            sensor_id = parts[1]
            obs_time = datetime.fromtimestamp(float(parts[2]))

            sensor_values = parse_sensor_data(format_spec, parts)
            if not sensor_values:
                print(f"No valid sensor data in format '{format_spec}': {payload}")
                return
        
        # temporarily indented
        ###############################################
        query, values = build_insert_query(sensor_id, obs_time, sensor_values)

        with psycopg2.connect(
            host=PG_HOST,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                # Write data to observations table
                cur.execute(query, values)

                # Update update_status table
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
        print(f"Error processing message: {msg.payload}")
        print(e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
