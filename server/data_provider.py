import random
import asyncio

async def get_data():
    # Simulate some async data fetching (e.g., querying a database)
    await asyncio.sleep(0)  # just an example async placeholder
    
    value = random.randint(1, 100)
    return {"value": value}


if __name__ == "__main__":
    result = asyncio.run(get_data())
    print(result)