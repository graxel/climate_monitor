import asyncio
import json
import ssl

import websockets
from dotenv import load_dotenv

from ws_data_provider import get_data

load_dotenv()


CONNECTED = set()

    certfile=CERTFILE,
    keyfile=KEYFILE
    
async def broadcast_data():
    while True:
        data = await get_data()
        message = json.dumps(data)
        if CONNECTED:
            await asyncio.gather(*(ws.send(message) for ws in CONNECTED))
        await asyncio.sleep(5)

async def handler(websocket):
    CONNECTED.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED.remove(websocket)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    certfile=CERTFILE,
    keyfile=KEYFILE
)

async def main():
    async with websockets.serve(
        handler,
        host="0.0.0.0",
        port=6789,
        ssl=ssl_context
    ):
        print("Secure WebSocket server started")
        await broadcast_data()

if __name__ == "__main__":
    asyncio.run(main())
