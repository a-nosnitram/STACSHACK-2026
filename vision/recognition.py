import cv2
from vision.pose_recognition import match_expected_pose, squat_critical_sets


def handle_pose_recognition(frame, result, db, pose_name, ui_state):
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
                db,
                pose_name,
                result.pose_landmarks[0],
                p_min=0.7,
                v_min=None,
                min_points=10,
                critical_sets=squat_critical_sets(),
                use_z=True,
            )

            if out is None:
                match_text = f"{pose_name}: not enough usable landmarks"
            else:
                dist, used = out
                dist_value = dist
                matched = dist < 0.2  # Tweak this threshold (e.g. 0.15 - 0.3)
                match_text = f"{pose_name} dist:{dist:.3f} pts:{used}/33 " + (
                    "MATCH" if matched else ""
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
