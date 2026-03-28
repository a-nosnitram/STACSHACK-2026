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
    """
    Side-view dead bug: pick the side with better confidence for the chain:
    shoulder, elbow, wrist, hip, knee, ankle.
    """
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


def dead_bug_metrics(normalized_landmarks, *, p_min=0.5):
    """
    Side-view dead bug (lying on back):
    - torso_flat: shoulder->hip line close to horizontal
    - knee_angle: angle(hip-knee-ankle) near 90°
    - hip_angle: angle(shoulder-hip-knee) near 90°
    - elbow_angle: angle(shoulder-elbow-wrist) near 180° (arm straight)
    - wrist_dx: |wrist.x - shoulder.x| small (arm stacked up)
    - wrist_above: (shoulder.y - wrist.y) positive (wrist above shoulder)
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

    # Torso flat (same computation as plank): angle to horizontal (0 = perfectly horizontal).
    dx = hx - sx
    dy = hy - sy
    torso_flat = math.degrees(math.atan2(abs(dy), abs(dx) + 1e-9))

    knee_angle = angle_deg(hip, knee, ankle)
    hip_angle = angle_deg(shoulder, hip, knee)
    elbow_angle = angle_deg(shoulder, elbow, wrist)

    wrist_dx = abs(wrist[0] - shoulder[0])
    wrist_above = shoulder[1] - wrist[1]  # >0 means wrist is above shoulder in image coords

    return {
        "side": side,
        "torso_flat": torso_flat,
        "knee_angle": knee_angle,
        "hip_angle": hip_angle,
        "elbow_angle": elbow_angle,
        "wrist_dx": wrist_dx,
        "wrist_above": wrist_above,
    }


def dead_bug_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    torso_flat_max=20.0,
    knee_angle_target=90.0,
    knee_angle_err_max=25.0,
    hip_angle_target=90.0,
    hip_angle_err_max=30.0,
    elbow_angle_min=155.0,
    wrist_dx_max=0.20,
    wrist_above_min=0.10,
    # soft ranges for match index
    torso_flat_soft=10.0,
    knee_err_soft=15.0,
    hip_err_soft=20.0,
    elbow_soft=20.0,
    wrist_dx_soft=0.10,
    wrist_above_soft=0.08,
):
    """
    Returns (matched_bool, match_index_0_to_1).

    Simple constraints (side view):
    - torso flat-ish
    - knee and hip angles near 90°
    - arm straight-ish and stacked up (wrist above shoulder)
    """
    m = dead_bug_metrics(normalized_landmarks, p_min=p_min)
    if m is None:
        return (False, 0.0)

    knee_err = abs(m["knee_angle"] - knee_angle_target)
    hip_err = abs(m["hip_angle"] - hip_angle_target)

    matched = (
        m["torso_flat"] <= torso_flat_max
        and knee_err <= knee_angle_err_max
        and hip_err <= hip_angle_err_max
        and m["elbow_angle"] >= elbow_angle_min
        and m["wrist_dx"] <= wrist_dx_max
        and m["wrist_above"] >= wrist_above_min
    )

    torso_score = score_below(m["torso_flat"], torso_flat_max, torso_flat_soft)
    knee_score = score_below_abs(knee_err, knee_angle_err_max, knee_err_soft)
    hip_score = score_below_abs(hip_err, hip_angle_err_max, hip_err_soft)
    elbow_score = score_below(180.0 - m["elbow_angle"], 180.0 - elbow_angle_min, elbow_soft)
    wrist_dx_score = score_below(m["wrist_dx"], wrist_dx_max, wrist_dx_soft)
    wrist_up_score = score_below(0.0 - m["wrist_above"], 0.0 - wrist_above_min, wrist_above_soft)

    match_index = (
        0.25 * torso_score
        + 0.20 * knee_score
        + 0.20 * hip_score
        + 0.15 * elbow_score
        + 0.10 * wrist_dx_score
        + 0.10 * wrist_up_score
    )

    return (matched, match_index)
