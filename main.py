# main.py

import asyncio
import websockets

from phone_cam.server import process_stream
from vision.main import run_vision


async def main():
    server = await websockets.serve(process_stream, "0.0.0.0", 8765)

    print("Server running...")

    await run_vision()  # runs your mediapipe loop


asyncio.run(main())
