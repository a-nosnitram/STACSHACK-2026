# vision/main.py

import mediapipe as mp
import cv2
import time
from pathlib import Path
from vision.draw_landmarks import draw_landmarks
from vision.pose_recognition import (
    load_poses,
)
from vision.capture_pose import handle_countdown_and_capture
from vision.state import clients, ui_state
import asyncio

MODEL_PATH = (
    Path(__file__).resolve().parent / "../models" / "pose_landmarker_heavy.task"
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

DB_PATH = Path(__file__).resolve().parent / "poses.json"
db = load_poses(DB_PATH)

POSE_NAME = "squat"  # for now

COUNTDOWN_SEC = 5

recognition_active = False


async def run_vision():
    with PoseLandmarker.create_from_options(options) as landmarker:
        while True:
            now_ms = int((time.monotonic() - start_time) * 1000)
            if not clients:
                await asyncio.sleep(0.01)
                continue

            for client_id, frame in clients.items():
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                timestamp_ms = int((time.monotonic() - start_time) * 1000)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                frame = draw_landmarks(frame, result)
                frame = handle_countdown_and_capture(
                    frame, result, now_ms, ui_state, db, POSE_NAME, DB_PATH
                )
                cv2.imshow(f"Client {client_id}", frame)

            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
            if key == ord("c") and not ui_state["countdown_active"]:
                ui_state["countdown_active"] = True
                ui_state["countdown_start_ms"] = now_ms

            await asyncio.sleep(0)

        cv2.destroyAllWindows()
        #     # Recognition (toggle with 'r') ---
        #     match_text = "Recognition: OFF (press 'r')"
        #     matched = False
        #     dist_value = None

        #     if recognition_active:
        #         if len(result.pose_landmarks) == 0:
        #             match_text = "squat: (no person)"
        #         else:
        #             out = match_expected_pose(
        #                 db,
        #                 "squat",
        #                 result.pose_landmarks[0],
        #                 p_min=0.7,
        #                 v_min=None,
        #                 min_points=10,
        #                 critical_sets=squat_critical_sets(),
        #                 use_z=True,
        #             )

        #             if out is None:
        #                 match_text = "squat: not enough usable landmarks"
        #             else:
        #                 dist, used = out
        #                 dist_value = dist
        #                 matched = dist < 3  # tune this threshold
        #                 match_text = f"squat dist:{dist:.3f} pts:{used}/33 " + (
        #                     "MATCH" if matched else ""
        #                 )

        #     # countown + capture logic
        #     if countdown_active:
        #         elapsed_ms = now_ms - countdown_start_ms
        #         remaining = COUNTDOWN_SEC - int(elapsed_ms / 1000)

        #         cv2.putText(
        #             frame,
        #             f"CAPTURING {POSE_NAME} IN: {max(0, remaining)}",
        #             (30, 140),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             1.2,
        #             (0, 255, 255),
        #             3,
        #         )

        #         if elapsed_ms >= COUNTDOWN_SEC * 1000:
        #             ok = capture_pose_template(result, db, POSE_NAME, path=DB_PATH)

        #             countdown_active = False

        #             saved_banner_active = True
        #             saved_banner_until_ms = now_ms + 1500
        #             saved_banner_text = "POSE SAVED!" if ok else "CAPTURE FAILED"
        #             saved_banner_color = (0, 255, 0) if ok else (0, 0, 255)

        #             if ok:
        #                 print(
        #                     f"Captured '{POSE_NAME}'. Total samples: {len(db.get(POSE_NAME, []))}"
        #                 )
        #             else:
        #                 print("Capture failed (no person / low confidence).")

        #     if saved_banner_active:
        #         cv2.putText(
        #             frame,
        #             saved_banner_text,
        #             (30, 200),
        #             cv2.FONT_HERSHEY_SIMPLEX,
        #             1.4,
        #             saved_banner_color,
        #             4,
        #         )
        #         if now_ms >= saved_banner_until_ms:
        #             saved_banner_active = False

        #     # ---- UI ----
        #     cv2.putText(
        #         frame,
        #         f"FPS: {1 / max(1e-6, (end_time - start_time)):.2f}",
        #         (10, 30),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         1,
        #         (0, 255, 0),
        #         2,
        #     )
        #     cv2.putText(
        #         frame,
        #         f"Press 'c' to start {COUNTDOWN_SEC}s capture: {POSE_NAME}",
        #         (10, 65),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         0.7,
        #         (255, 255, 255),
        #         2,
        #     )
        #     cv2.putText(
        #         frame,
        #         "Press 'r' to toggle recognition",
        #         (10, 90),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         0.7,
        #         (255, 255, 255),
        #         2,
        #     )
        #     cv2.putText(
        #         frame,
        #         match_text,
        #         (10, 120),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         0.8,
        #         (0, 200, 255),
        #         2,
        #     )

        #     # Big MATCH text in the middle when recognition is on and we match squat.
        #     if recognition_active and matched:
        #         text = "MATCH"
        #         font = cv2.FONT_HERSHEY_SIMPLEX
        #         scale = 3.0
        #         thickness = 8
        #         (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        #         x = (frame.shape[1] - tw) // 2
        #         y = (frame.shape[0] + th) // 2
        #         cv2.putText(frame, text, (x, y), font, scale, (0, 0, 0), thickness + 4)
        #         cv2.putText(frame, text, (x, y), font, scale, (0, 255, 0), thickness)

        #     # Big distance in the middle (smaller than MATCH)
        #     if recognition_active and dist_value is not None:
        #         text = f"{dist_value:.3f}"
        #         font = cv2.FONT_HERSHEY_SIMPLEX
        #         scale = 1.6
        #         thickness = 4
        #         (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        #         x = (frame.shape[1] - tw) // 2
        #         # place slightly above center so it doesn't overlap MATCH as much
        #         y = (frame.shape[0] + th) // 2 - 70
        #         cv2.putText(frame, text, (x, y), font, scale, (0, 0, 0), thickness + 3)
        #         cv2.putText(
        #             frame, text, (x, y), font, scale, (255, 255, 255), thickness
        #         )

        #     cv2.imshow("MediaPipe Pose Landmarker", frame)

        #     # ---- Keys ----
        #     key = cv2.waitKey(5) & 0xFF
        #     if key == 27:  # ESC
        #         break
        #     if key == ord("c") and not countdown_active:
        #         countdown_active = True
        #         countdown_start_ms = now_ms
        #         saved_banner_active = False
        #     if key == ord("r"):
        #         recognition_active = not recognition_active
        #         print(f"Recognition {'ON' if recognition_active else 'OFF'}")

        # cv2.destroyAllWindows()
        # #     cv2.putText(frame, f'FPS: {1 / (end_time - start_time):.2f}', (10, 30),
        # #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # #     cv2.imshow('MediaPipe Pose Landmarker', frame)

        # #     if cv2.waitKey(5) & 0xFF == 27:
        #         break

        # cap.release()
        # cv2.destroyAllWindows()
