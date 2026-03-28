# vision/main.py

import mediapipe as mp
import cv2
import time
from pathlib import Path
from vision.draw_landmarks import draw_landmarks
from vision.recognition import handle_pose_recognition
from vision.state import clients, ui_state
import asyncio
from shared.bus import game_to_vision, vision_to_game

MODEL_PATH = (
    Path(__file__).resolve().parent /
    "../models" / "pose_landmarker_heavy.task"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "no MediaPipe pose landmarker model at "
        f"{MODEL_PATH} :( \n Download a .task model and place it there."
    )


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the video mode:
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=VisionRunningMode.VIDEO,
)

start_time = time.monotonic()


COUNTDOWN_SEC = 5

recognition_active = False


async def run_vision():
    with PoseLandmarker.create_from_options(options) as landmarker:
        while True:
            now_ms = int((time.monotonic() - start_time) * 1000)
            # read from bus
            while not game_to_vision.empty():
                msg = await game_to_vision.get()
                print(f"Vision received message: {msg}")
                if msg["type"] == "start_match":
                    poses = msg["poses"]
                    print(f"Starting match with poses: {poses}")
                    coutdown = msg["rounds_ms"] // 1000
                    print(f"Countdown: {coutdown} seconds")

            if not clients:
                await asyncio.sleep(0.01)
                continue

            for client_id, frame in clients.items():
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                timestamp_ms = int((time.monotonic() - start_time) * 1000)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                frame = draw_landmarks(frame, result)

                for pose in poses:
                    frame, matched, dist = handle_pose_recognition(
                        frame, result, pose, ui_state
                    )

                cv2.imshow(f"Client {client_id}", frame)

            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
            if key == ord("c") and not ui_state["countdown_active"]:
                ui_state["countdown_active"] = True
                ui_state["countdown_start_ms"] = now_ms
            if key == ord("r"):
                ui_state["recognition_active"] = not ui_state["recognition_active"]

            await asyncio.sleep(0)

        cv2.destroyAllWindows()
