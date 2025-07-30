import asyncio
import websockets
import json
import ssl

from ws_data_provider import get_data

CONNECTED = set()

async def broadcast_data():
    while True:
        data = await get_data()
        message = json.dumps(data)
        if CONNECTED:
            await asyncio.gather(*(ws.send(message) for ws in CONNECTED))
        await asyncio.sleep(1)

async def handler(websocket, path):
    print(f"New connection on path: {path}")  # Debug to confirm path is received
    if path != "/ws/":
        # Optionally reject connections on unexpected paths
        await websocket.close(code=1008, reason="Invalid path")
        return

    CONNECTED.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED.remove(websocket)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    certfile='/etc/letsencrypt/live/data.kevingrazel.com/fullchain.pem',
    keyfile='/etc/letsencrypt/live/data.kevingrazel.com/privkey.pem'
)

async def main():
    async with websockets.serve(
        handler,
        host="0.0.0.0",
        port=6789,
        ssl=ssl_context
    ):
        print("Secure WebSocket server started on wss://data.kevingrazel.com/ws/")
        await broadcast_data()

if __name__ == "__main__":
    asyncio.run(main())
