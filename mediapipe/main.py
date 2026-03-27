import vision.hand_tracker as hand_tracker
import mediapipe as mp
import cv2
import time
from pathlib import Path
from the_magic import the_calculation, the_more_forgiving_calculation


MODEL_PATH = Path(__file__).resolve().parent / \
    "models" / "pose_landmarker_heavy.task"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "no MediaPipe pose landmarker model at "
        f"{MODEL_PATH} :( \n Download a .task model and place it there."
    )

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
)
