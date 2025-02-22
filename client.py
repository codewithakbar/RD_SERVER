import asyncio
import socket
import mss
import io
import websockets
from PIL import Image

# Server WebSocket URL
SERVER_WS_URL = "ws://192.168.1.161:5050/ws/capture"
KEY = socket.gethostname()  # Unique identifier (computer name)


async def capture_and_stream():
    """Capture the screen and stream frames via WebSockets."""
    async with websockets.connect(SERVER_WS_URL) as websocket:
        await websocket.send(KEY)  # Send session key first
        print("[*] Connected to WebSocket server")

        with mss.mss() as sct:
            while True:
                # Capture screen
                screenshot = sct.grab(sct.monitors[1])
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                # Compress image
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=50)
                buffer.seek(0)

                # Send to WebSocket
                await websocket.send(buffer.getvalue())
                print("[*] Frame sent")

                await asyncio.sleep(0.1)  # Adjust for real-time performance


async def main():
    while True:
        try:
            await capture_and_stream()
        except Exception as e:
            print("[!] Connection lost. Reconnecting...")
            await asyncio.sleep(3)  # Reconnect delay


if __name__ == "__main__":
    asyncio.run(main())
