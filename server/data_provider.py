import random
import asyncio
from datetime import datetime


async def get_data():
    # Simulate some async data fetching (e.g., querying a database)
    await asyncio.sleep(0)  # just an example async placeholder
    
    value = random.randint(20, 27)
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sensor_data": {
            "office_temp": value,
            "office_hum": 45,
            "kitchen_temp": value + 2,
            "kitchen_hum": 50,
            "closet_temp": 25,
            "closet_hum": 48,
            "bedroom_temp": 23,
            "bedroom_hum": 51
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
    return {"data": data}


if __name__ == "__main__":
    result = asyncio.run(get_data())
    print(result)