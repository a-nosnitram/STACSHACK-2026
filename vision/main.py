# vision/main.py

import mediapipe as mp
import cv2
import time
from pathlib import Path
from vision.draw_landmarks import draw_landmarks
from vision.recognition import handle_pose_recognition
from vision.state import clients, ui_state, match
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


last_timestamp_ms = 0
frame_count = 0


async def run_vision():
    global last_timestamp_ms
    with PoseLandmarker.create_from_options(options) as landmarker:
        while True:
            now_ms = int((time.monotonic() - start_time) * 1000)
            # read from bus
            while not game_to_vision.empty():
                msg = await game_to_vision.get()
                print(f"Vision received message: {msg}")
                match.handle_message(msg, now_ms)

            if not clients:
                await asyncio.sleep(0.01)
                continue

            visible_clients: set[int] = set()
            for client_id, frame in list(clients.items()):
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                timestamp_ms = max(now_ms, last_timestamp_ms + 1)
                last_timestamp_ms = timestamp_ms
                result = landmarker.detect_for_video(mp_image, timestamp_ms)
                frame = draw_landmarks(frame, result)
                if result.pose_landmarks:
                    visible_clients.add(client_id)

                if match.match_active and match.poses and not match.awaiting_players:
                    elapsed = now_ms - match.round_start_ms
                    in_prep = elapsed < match.prep_ms
                    in_hold = match.prep_ms <= elapsed < (
                        match.prep_ms + match.hold_ms)

                    ui_state["recognition_active"] = in_hold
                    current_pose = match.poses[match.round_index]
                    if in_hold:
                        frame, matched, score = handle_pose_recognition(
                            frame, result, current_pose, ui_state
                        )
                        if score is not None:
                            match.total_scores[client_id] = match.total_scores.get(
                                client_id, 0.0) + score
                            match.sample_counts[client_id] = match.sample_counts.get(
                                client_id, 0) + 1
                    else:
                        frame, _matched, _score = handle_pose_recognition(
                            frame, result, current_pose, ui_state
                        )

                    # HOLD PHASE
                    phase_text = "Get ready" if in_prep else "Hold pose"
                    time_left_ms = (
                        match.prep_ms -
                        elapsed if in_prep else (
                            match.prep_ms + match.hold_ms - elapsed)
                    )
                    time_left = max(0, int(time_left_ms / 1000))
                    colour = (0, 0, 255) if in_hold else (255, 0, 0)
                    cv2.putText(
                        frame,
                        f"{phase_text}: {current_pose} ({time_left}s)",
                        (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        colour,
                        2,
                    )

                # WAITING
                elif match.match_active and match.poses and match.awaiting_players:
                    cv2.putText(
                        frame,
                        f"Waiting for both players ({len(visible_clients)}/{match.expected_players})",
                        (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 200, 255),
                        2,
                    )

                cv2.imshow(f"Client {client_id}", frame)

            # handle round timing and results
            if match.match_active and match.poses and match.awaiting_players:
                if len(visible_clients) >= match.expected_players:
                    match.awaiting_players = False
                    match.round_start_ms = now_ms
                    match.total_scores = {}
                    match.sample_counts = {}

            if match.match_active and match.poses and not match.awaiting_players:
                elapsed = now_ms - match.round_start_ms
                if elapsed >= (match.prep_ms + match.hold_ms):
                    winner = None
                    avg_scores = {
                        client_id: (
                            match.total_scores[client_id] /
                            match.sample_counts.get(client_id, 1)
                        )
                        for client_id in match.total_scores
                    }
                    if avg_scores:
                        winner = max(avg_scores, key=avg_scores.get)
                    await vision_to_game.put(
                        {
                            "type": "round_result",
                            "round": match.round_index + 1,
                            "pose": match.poses[match.round_index],
                            "winner": winner,
                            "scores": avg_scores,
                        }
                    )
                    print(
                        f"Round {match.round_index + 1} result: winner=Client {winner} with scores {avg_scores}")
                    match.round_index += 1
                    match.total_scores = {}
                    match.sample_counts = {}
                    match.round_start_ms = now_ms
                    if match.round_index >= len(match.poses):
                        match.match_active = False
                        match.awaiting_players = False
                        ui_state["recognition_active"] = False
                        await vision_to_game.put(
                            {"type": "match_complete", "poses": match.poses}
                        )

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
