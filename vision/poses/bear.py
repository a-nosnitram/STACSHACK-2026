# vision/poses/bear.py
# Simple, robust bear pose (quadruped) detector.
#
# Checks (minimal but solid):
# - shoulders stacked over wrists (x alignment)
# - hips stacked over knees (x alignment)
# - hip angle ~ 90° (shoulder-hip-knee)
# - knee angle ~ 90° (hip-knee-ankle)
# - arms fairly straight (shoulder-elbow-wrist)
# - torso roughly parallel to floor (shoulder-hip line ~ horizontal)
#
# Returns: (matched_bool, match_index_0_to_1)

import math

from vision.pose_utils import (
    LA,
    LE,
    LH,
    LK,
    LS,
    LW,
    RA,
    RE,
    RH,
    RK,
    RS,
    RW,
    angle_deg,
    get,
    presence,
    score_below,
    score_below_abs,
    xy,
)


def _choose_side(lms, p_min=0.5):
    """Pick L/R based on presence of shoulder, elbow, wrist, hip, knee, ankle."""
    left_ok = (
        presence(get(lms, LS)) >= p_min
        and presence(get(lms, LE)) >= p_min
        and presence(get(lms, LW)) >= p_min
        and presence(get(lms, LH)) >= p_min
        and presence(get(lms, LK)) >= p_min
        and presence(get(lms, LA)) >= p_min
    )
    right_ok = (
        presence(get(lms, RS)) >= p_min
        and presence(get(lms, RE)) >= p_min
        and presence(get(lms, RW)) >= p_min
        and presence(get(lms, RH)) >= p_min
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
        presence(get(lms, LS))
        + presence(get(lms, LE))
        + presence(get(lms, LW))
        + presence(get(lms, LH))
        + presence(get(lms, LK))
        + presence(get(lms, LA))
    )
    right_score = (
        presence(get(lms, RS))
        + presence(get(lms, RE))
        + presence(get(lms, RW))
        + presence(get(lms, RH))
        + presence(get(lms, RK))
        + presence(get(lms, RA))
    )
    return "L" if left_score >= right_score else "R"


def bear_metrics(normalized_landmarks, *, p_min=0.5):
    """
    Returns metrics for the most reliable side:
      - torso_flat: deg away from horizontal of shoulder->hip (0 = horizontal)
      - shoulder_wrist_dx: |shoulder.x - wrist.x|
      - hip_knee_dx: |hip.x - knee.x|
      - elbow_angle: angle(shoulder-elbow-wrist) (straight ~180)
      - hip_angle: angle(shoulder-hip-knee) (~90)
      - knee_angle: angle(hip-knee-ankle) (~90)
    """
    lms = normalized_landmarks
    side = _choose_side(lms, p_min=p_min)
    if side is None:
        return None

    if side == "L":
        shoulder = xy(get(lms, LS))
        elbow = xy(get(lms, LE))
        wrist = xy(get(lms, LW))
        hip = xy(get(lms, LH))
        knee = xy(get(lms, LK))
        ankle = xy(get(lms, LA))
    else:
        shoulder = xy(get(lms, RS))
        elbow = xy(get(lms, RE))
        wrist = xy(get(lms, RW))
        hip = xy(get(lms, RH))
        knee = xy(get(lms, RK))
        ankle = xy(get(lms, RA))

    sx, sy = shoulder
    hx, hy = hip

    dx = hx - sx
    dy = hy - sy
    torso_flat = math.degrees(math.atan2(abs(dy), abs(dx) + 1e-9))

    shoulder_wrist_dx = abs(shoulder[0] - wrist[0])
    hip_knee_dx = abs(hip[0] - knee[0])

    elbow_angle = angle_deg(shoulder, elbow, wrist)
    hip_angle = angle_deg(shoulder, hip, knee)
    knee_angle = angle_deg(hip, knee, ankle)

    return {
        "side": side,
        "torso_flat": torso_flat,
        "shoulder_wrist_dx": shoulder_wrist_dx,
        "hip_knee_dx": hip_knee_dx,
        "elbow_angle": elbow_angle,
        "hip_angle": hip_angle,
        "knee_angle": knee_angle,
    }


def bear_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    torso_flat_max=25.0,
    shoulder_wrist_dx_max=0.18,
    hip_knee_dx_max=0.20,
    elbow_angle_min=150.0,
    hip_angle_target=90.0,
    hip_angle_err_max=35.0,
    knee_angle_target=90.0,
    knee_angle_err_max=35.0,
    
    torso_soft=12.0,
    stack_soft=0.10,
    elbow_soft=20.0,
    hip_err_soft=20.0,
    knee_err_soft=20.0,
):
    """
    Returns (matched_bool, match_index_0_to_1).
    """
    m = bear_metrics(normalized_landmarks, p_min=p_min)
    if m is None:
        return (False, 0.0)

    hip_err = abs(m["hip_angle"] - hip_angle_target)
    knee_err = abs(m["knee_angle"] - knee_angle_target)

    matched = (
        m["torso_flat"] <= torso_flat_max
        and m["shoulder_wrist_dx"] <= shoulder_wrist_dx_max
        and m["hip_knee_dx"] <= hip_knee_dx_max
        and m["elbow_angle"] >= elbow_angle_min
        and hip_err <= hip_angle_err_max
        and knee_err <= knee_angle_err_max
    )

    torso_score = score_below(m["torso_flat"], torso_flat_max, torso_soft)
    shoulder_stack_score = score_below(m["shoulder_wrist_dx"], shoulder_wrist_dx_max, stack_soft)
    hip_stack_score = score_below(m["hip_knee_dx"], hip_knee_dx_max, stack_soft)

    elbow_err = 180.0 - m["elbow_angle"]
    elbow_err_max = 180.0 - elbow_angle_min
    elbow_score = score_below(elbow_err, elbow_err_max, elbow_soft)

    hip_score = score_below_abs(hip_err, hip_angle_err_max, hip_err_soft)
    knee_score = score_below_abs(knee_err, knee_angle_err_max, knee_err_soft)

    match_index = (
        0.20 * torso_score
        + 0.20 * shoulder_stack_score
        + 0.15 * hip_stack_score
        + 0.15 * elbow_score
        + 0.15 * hip_score
        + 0.15 * knee_score
    )

    return (matched, float(match_index))
