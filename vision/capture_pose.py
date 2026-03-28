import cv2
from vision.pose_recognition import capture_pose_template


def handle_countdown_and_capture(
    frame,
    result,
    now_ms: int,
    ui: dict,
    db: dict,
    pose_name: str,
    db_path,
    countdown_sec: int = 5,
):
    """Handles the capture countdown and save banner."""

    # Countdown logic
    if ui["countdown_active"]:
        elapsed_ms = now_ms - ui["countdown_start_ms"]
        remaining = countdown_sec - int(elapsed_ms / 1000)

        cv2.putText(
            frame,
            f"CAPTURING {pose_name} IN: {max(0, remaining)}",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 255),
            3,
        )

        if elapsed_ms >= countdown_sec * 1000:
            ok = capture_pose_template(result, db, pose_name, path=db_path)

            # Update dictionary
            ui["countdown_active"] = False
            ui["saved_banner_active"] = True
            ui["saved_banner_until_ms"] = now_ms + 1500
            ui["saved_banner_text"] = "POSE SAVED!" if ok else "CAPTURE FAILED"
            ui["saved_banner_color"] = (0, 255, 0) if ok else (0, 0, 255)

    # Banner logic
    if ui["saved_banner_active"]:
        cv2.putText(
            frame,
            ui["saved_banner_text"],
            (30, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            ui["saved_banner_color"],
            4,
        )

        if now_ms >= ui["saved_banner_until_ms"]:
            ui["saved_banner_active"] = False

    return frame
