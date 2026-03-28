import math

from vision.pose_utils import (
    LA,
    LH,
    LS,
    LW,
    RA,
    RH,
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
    Choose left or right side based on presence of (shoulder, hip, wrist, ankle).
    Returns "L", "R", or None.
    """
    left_ok = (
        presence(get(lms, LS)) >= p_min
        and presence(get(lms, LH)) >= p_min
        and presence(get(lms, LW)) >= p_min
        and presence(get(lms, LA)) >= p_min
    )
    right_ok = (
        presence(get(lms, RS)) >= p_min
        and presence(get(lms, RH)) >= p_min
        and presence(get(lms, RW)) >= p_min
        and presence(get(lms, RA)) >= p_min
    )

    if not left_ok and not right_ok:
        return None
    if left_ok and not right_ok:
        return "L"
    if right_ok and not left_ok:
        return "R"

    left_score = (
        presence(get(lms, LS)) + presence(get(lms, LH)) + presence(get(lms, LW)) + presence(get(lms, LA))
    )
    right_score = (
        presence(get(lms, RS)) + presence(get(lms, RH)) + presence(get(lms, RW)) + presence(get(lms, RA))
    )
    return "L" if left_score >= right_score else "R"


def plank_metrics(normalized_landmarks, *, p_min=0.5):
    """
    Returns metrics for the most reliable side:
      - torso_flat: degrees away from horizontal (0 = perfectly flat)
      - hip_angle: angle(shoulder-hip-ankle) (180 = straight body line)
      - wrist_under_shoulder_dx: |wrist.x - shoulder.x|
      - hip_drop: hip.y - shoulder.y (pike => negative, sag => positive)
    """
    lms = normalized_landmarks
    side = _choose_side(lms, p_min=p_min)
    if side is None:
        return None

    if side == "L":
        shoulder = xy(get(lms, LS))
        hip = xy(get(lms, LH))
        wrist = xy(get(lms, LW))
        ankle = xy(get(lms, LA))
    else:
        shoulder = xy(get(lms, RS))
        hip = xy(get(lms, RH))
        wrist = xy(get(lms, RW))
        ankle = xy(get(lms, RA))

    sx, sy = shoulder
    hx, hy = hip
    wx, wy = wrist

    # Torso flat: shoulder->hip line should be close to horizontal in SIDE view.
    # Compute angle to horizontal (0 deg = horizontal).
    dx = hx - sx
    dy = hy - sy
    torso_flat = math.degrees(math.atan2(abs(dy), abs(dx) + 1e-9))

    # Whole-body straightness at the hip
    hip_angle = angle_deg(shoulder, hip, ankle)

    # Wrist under shoulder: x alignment in SIDE view.
    wrist_under_shoulder_dx = abs(wx - sx)

    # Hip relative to shoulder.
    hip_drop = hy - sy

    return {
        "side": side,
        "torso_flat": torso_flat,
        "hip_angle": hip_angle,
        "wrist_under_shoulder_dx": wrist_under_shoulder_dx,
        "hip_drop": hip_drop,
    }

def plank_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    torso_flat_max=20.0,            # deg away from horizontal
    hip_angle_min=160.0,            # shoulder-hip-ankle should be near straight line
    wrist_under_shoulder_dx_max=0.15,  # normalized units
    hip_drop_min=-0.05,             # hip not too far ABOVE shoulder (pike)
    hip_drop_max=0.25,              # hip not too far BELOW shoulder (sag)
    # soft ranges for match index (how quickly score drops near threshold)
    torso_flat_soft=10.0,
    hip_angle_soft=15.0,
    wrist_dx_soft=0.08,
    hip_drop_soft=0.10,
):
    """
    Returns (matched_bool, match_index_0_to_1).

    SIDE view assumptions:
    - torso_flat small => torso looks flat/horizontal
    - wrist x close to shoulder x => wrist stacked under shoulder
    - hip_drop near 0 => hips not sagging/piking too much
    """
    m = plank_metrics(normalized_landmarks, p_min=p_min)
    if m is None:
        return (False, 0.0)

    matched = (
        m["torso_flat"] <= torso_flat_max
        and m["hip_angle"] >= hip_angle_min
        and m["wrist_under_shoulder_dx"] <= wrist_under_shoulder_dx_max
        and hip_drop_min <= m["hip_drop"] <= hip_drop_max
    )

    torso_score = score_below(m["torso_flat"], torso_flat_max, torso_flat_soft)
    hip_angle_err = 180.0 - m["hip_angle"]
    hip_angle_err_max = 180.0 - hip_angle_min
    hip_angle_score = score_below(hip_angle_err, hip_angle_err_max, hip_angle_soft)
    wrist_score = score_below(m["wrist_under_shoulder_dx"], wrist_under_shoulder_dx_max, wrist_dx_soft)
    hip_high_err = max(0.0, hip_drop_min - m["hip_drop"])
    hip_low_err = max(0.0, m["hip_drop"] - hip_drop_max)
    hip_band_err = hip_high_err + hip_low_err
    hip_score = score_below_abs(hip_band_err, 0.0, hip_drop_soft)

    match_index = 0.40 * torso_score + 0.25 * hip_angle_score + 0.20 * wrist_score + 0.15 * hip_score
    return (matched, match_index)
