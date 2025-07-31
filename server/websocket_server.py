import os
import asyncio
import json
import ssl

import websockets
from dotenv import load_dotenv

from ws_data_provider import get_data

load_dotenv()


CONNECTED = set()

CERTFILE = os.getenv('CERTFILE')
KEYFILE = os.getenv('KEYFILE')

async def broadcast_data():
    while True:
        data = await get_data()
        message = json.dumps(data)
        if CONNECTED:
            to_remove = set()
            for ws in CONNECTED:
                try:
                    await ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    to_remove.add(ws)
            for ws in to_remove:
                CONNECTED.remove(ws)
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
    server = await websockets.serve(
        handler,
        host="0.0.0.0",
        port=6789,
        ssl=ssl_context
    )
    print("Secure WebSocket server started")
    broadcaster_task = asyncio.create_task(broadcast_data())
    await server.wait_closed()
    broadcaster_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
