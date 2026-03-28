import asyncio
import websockets
import cv2
import numpy as np
import base64

client_id_counter = 0


async def process_stream(websocket):
    global client_id_counter
    client_id = client_id_counter
    client_id_counter += 1

    print(f"Phone {client_id} connected!")

    async for message in websocket:
        try:
            if "," in message:
                message = message.split(",")[1]

            img_bytes = base64.b64decode(message)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            cv2.imshow(f"Phone {client_id}", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except Exception as e:
            print(f"Error (client {client_id}):", e)

    print(f"Phone {client_id} disconnected")
    cv2.destroyWindow(f"Phone {client_id}")


async def main():
    async with websockets.serve(process_stream, "0.0.0.0", 8765):
        print("Server running...")
        await asyncio.Future()


asyncio.run(main())
