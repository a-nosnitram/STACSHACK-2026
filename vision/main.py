import mediapipe as mp
import cv2
import time
from pathlib import Path
import pyautogui
from draw_landmarks import draw_landmarks
from pose_recognition import load_poses, capture_pose, extract_features, best_match, print_most_visible_landmarks



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

DB_PATH = Path(__file__).resolve().parent / "poses.json"
db = load_poses(DB_PATH)

POSE_NAME = "squat"  #for now

COUNTDOWN_SEC = 5
countdown_active = False
countdown_start_ms = 0

saved_banner_active = False
saved_banner_until_ms = 0

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
        now_ms = timestamp_ms

        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        end_time = time.monotonic()


        frame = draw_landmarks(frame, result)


        # countown + capture logic
        if countdown_active:
            elapsed_ms = now_ms - countdown_start_ms
            remaining = COUNTDOWN_SEC - int(elapsed_ms / 1000)

            cv2.putText(
                frame,
                f"CAPTURING {POSE_NAME} IN: {max(0, remaining)}",
                (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 255),
                3,
            )

            if elapsed_ms >= COUNTDOWN_SEC * 1000:
                # ok = capture_pose(result, db, POSE_NAME, path=DB_PATH)
                print_most_visible_landmarks(result, person_index=0, top_k=20, score="visibility")


                countdown_active = False

                saved_banner_active = True
                saved_banner_until_ms = now_ms + 1500

                # if ok:
                #     print(f"Captured '{POSE_NAME}'. Total samples: {len(db.get(POSE_NAME, []))}")
                # else:
                #     print("Capture failed (no person / low confidence).")

        if saved_banner_active:
            cv2.putText(
                frame,
                "POSE SAVED!",
                (30, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.4,
                (0, 255, 0),
                4,
            )
            if now_ms >= saved_banner_until_ms:
                saved_banner_active = False

        # ---- UI ----
        cv2.putText(
            frame,
            f"FPS: {1 / max(1e-6, (end_time - start_time)):.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Press 'c' to start {COUNTDOWN_SEC}s capture: {POSE_NAME}",
            (10, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        # if match_text:
        #     cv2.putText(
        #         frame,
        #         match_text,
        #         (10, 95),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         0.8,
        #         (0, 200, 255),
        #         2,
        #     )

        cv2.imshow("MediaPipe Pose Landmarker", frame)

        # ---- Keys ----
        key = cv2.waitKey(5) & 0xFF
        if key == 27:  # ESC
            break
        if key == ord("c") and not countdown_active:
            countdown_active = True
            countdown_start_ms = now_ms
            saved_banner_active = False

    cap.release()
    cv2.destroyAllWindows()
    #     cv2.putText(frame, f'FPS: {1 / (end_time - start_time):.2f}', (10, 30),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    #     cv2.imshow('MediaPipe Pose Landmarker', frame)

    #     if cv2.waitKey(5) & 0xFF == 27:
    #         break

    # cap.release()
    # cv2.destroyAllWindows()
