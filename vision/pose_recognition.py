# vision/pose_recognition.py
import math
from vision.squat import squat_match
import numpy as np

LS, RS = 11, 12  # shoulders
LE, RE = 13, 14  # elbows
LW, RW = 15, 16  # wrists
LH, RH = 23, 24  # hips
LK, RK = 25, 26  # knees
LA, RA = 27, 28  # ankles


def get(lms, i):
    return lms[i]


def xy(lm):
    return float(lm.x), float(lm.y)


def presence(lm):
    return float(getattr(lm, "presence", 1.0))


def angle_deg(a, b, c):
    """Angle ABC (degrees) using 2D points a,b,c = (x,y)."""
    ax, ay = a
    bx, by = b
    cx, cy = c

    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)

    ba_len = math.hypot(ba[0], ba[1])
    bc_len = math.hypot(bc[0], bc[1])
    denom = (ba_len * bc_len) + 1e-9

    cosv = (ba[0] * bc[0] + ba[1] * bc[1]) / denom
    cosv = max(-1.0, min(1.0, cosv))
    return math.degrees(math.acos(cosv))


def choose_side(lms, p_min=0.5):
    """
    Pick left or right leg based on presence of hip/knee/ankle.
    Returns "L" or "R" or None.
    """
    left_ok = (
        presence(get(lms, LH)) >= p_min
        and presence(get(lms, LK)) >= p_min
        and presence(get(lms, LA)) >= p_min
    )
    right_ok = (
        presence(get(lms, RH)) >= p_min
        and presence(get(lms, RK)) >= p_min
        and presence(get(lms, RA)) >= p_min
    )

    if not left_ok and not right_ok:
        return None
    if left_ok and not right_ok:
        return "L"
    if right_ok and not left_ok:
        return "R"

    left_score = (
        presence(get(lms, LH)) + presence(get(lms, LK)) + presence(get(lms, LA))
    )
    right_score = (
        presence(get(lms, RH)) + presence(get(lms, RK)) + presence(get(lms, RA))
    )
    return "L" if left_score >= right_score else "R"


def match_expected_pose(
    pose_name: str,
    live_person_landmarks,
) -> None | dict:
    if pose_name == "squat":
        return squat_match(live_person_landmarks)
    return None
