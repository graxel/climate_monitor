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
        try:
            data = await get_data()
            message = json.dumps(data)

            to_remove = set()

            if CONNECTED:
                for ws in CONNECTED:
                    try:
                        await ws.send(message)
                        # Send a ping frame to keep the connection alive and detect dead peers
                        await ws.ping()
                    except websockets.exceptions.ConnectionClosed:
                        # Mark websocket for removal if closed
                        to_remove.add(ws)
                    except Exception as e:
                        print(f"Error sending message to client: {e}")
                        to_remove.add(ws)

                # Remove closed connections after iteration
                for ws in to_remove:
                    CONNECTED.discard(ws)

            # Wait before next broadcast (adjust interval as needed)
            await asyncio.sleep(5)

        except Exception as e:
            # Catch and log errors in the broadcast loop so it doesn't crash silently
            print(f"Error in broadcast_data loop: {e}")
            # Avoid tight loop on persistent errors
            await asyncio.sleep(5)


async def handler(websocket):
    CONNECTED.add(websocket)
    try:
        # Since clients don't send messages, just wait until connection closes
        await websocket.wait_closed()
    except Exception as e:
        print(f"Exception in connection handler: {e}")
    finally:
        CONNECTED.discard(websocket)


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

    try:
        await server.wait_closed()
    finally:
        broadcaster_task.cancel()
        # Optionally, clean up connections on shutdown
        for ws in CONNECTED:
            await ws.close()
        CONNECTED.clear()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
