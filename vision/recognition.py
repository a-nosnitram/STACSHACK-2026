import cv2
from vision.pose_match import match_expected_pose


def handle_pose_recognition(frame, result, pose_name, ui_state):
    """Handles pose recognition and draws status on frame."""
    match_text = "Recognition: OFF (press 'r')"
    matched = False
    dist_value = None
    recognition_active = ui_state["recognition_active"]

    if recognition_active:
        if not result.pose_landmarks:
            match_text = f"{pose_name}: (no person)"
        else:
            out = match_expected_pose(
                pose_name,
                result.pose_landmarks[
                    0
                ],  # MediaPipe Tasks: already a list of 33 landmarks
            )

            if out is None:
                match_text = f"{pose_name}: not enough usable landmarks"
            else:
                matched, dist_value = out
                match_text = f"{pose_name} dist:{dist_value:.3f} " + (
                    "MATCH" if matched else "NO MATCH"
                )

    # Draw recognition status
    color = (0, 255, 0) if matched else (255, 255, 255)
    cv2.putText(
        frame,
        match_text,
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
    )
    return frame, matched, dist_value
