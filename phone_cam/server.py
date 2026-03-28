# phone-cam/server.py

import asyncio
import websockets
import cv2
import numpy as np
import base64
from vision.state import clients


def decode(message):
    if "," in message:
        message = message.split(",")[1]

    img_bytes = base64.b64decode(message)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


client_id_counter = 0


async def process_stream(websocket):
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1

    clients[client_id] = None
    print(f"Phone {client_id} connected")

    async for message in websocket:
        frame = decode(message)
        clients[client_id] = frame.copy()
