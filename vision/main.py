import mediapipe as mp
import cv2
import time
from pathlib import Path
import pyautogui
from draw_landmarks import draw_landmarks


MODEL_PATH = Path(__file__).resolve().parent / \
    "../models" / "pose_landmarker_heavy.task"

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
    running_mode=VisionRunningMode.VIDEO)

cap = cv2.VideoCapture(1)
start_time = time.monotonic()

# screen_width = pyautogui.size().width
# screen_height = pyautogui.size().height

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int((time.monotonic() - start_time) * 1000)

        pose_landmarks = landmarker.detect_for_video(mp_image, timestamp_ms)
        end_time = time.monotonic()

        frame = draw_landmarks(frame, pose_landmarks)

        cv2.putText(frame, f'FPS: {1 / (end_time - start_time):.2f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('MediaPipe Pose Landmarker', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
