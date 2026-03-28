import math

from vision.pose_utils import (
    LH,
    LS,
    LW,
    RH,
    RS,
    RW,
    get,
    presence,
    score_below,
    score_below_abs,
    xy,
)


def _choose_side(lms, p_min=0.5):
    """
    Choose left or right side based on presence of (shoulder, hip, wrist).
    Returns "L", "R", or None.
    """
    left_ok = (
        presence(get(lms, LS)) >= p_min
        and presence(get(lms, LH)) >= p_min
        and presence(get(lms, LW)) >= p_min
    )
    right_ok = (
        presence(get(lms, RS)) >= p_min
        and presence(get(lms, RH)) >= p_min
        and presence(get(lms, RW)) >= p_min
    )

    if not left_ok and not right_ok:
        return None
    if left_ok and not right_ok:
        return "L"
    if right_ok and not left_ok:
        return "R"

    left_score = presence(get(lms, LS)) + presence(get(lms, LH)) + presence(get(lms, LW))
    right_score = presence(get(lms, RS)) + presence(get(lms, RH)) + presence(get(lms, RW))
    return "L" if left_score >= right_score else "R"


def plank_metrics(normalized_landmarks, *, p_min=0.5):
    """
    Returns metrics for the most reliable side:
      - torso_flat: degrees away from horizontal (0 = perfectly flat)
      - wrist_under_shoulder_dx: |wrist.x - shoulder.x|
      - hip_drop: hip.y - shoulder.y (near 0 in a good plank)
    """
    lms = normalized_landmarks
    side = _choose_side(lms, p_min=p_min)
    if side is None:
        return None

    if side == "L":
        shoulder = xy(get(lms, LS))
        hip = xy(get(lms, LH))
        wrist = xy(get(lms, LW))
    else:
        shoulder = xy(get(lms, RS))
        hip = xy(get(lms, RH))
        wrist = xy(get(lms, RW))

    sx, sy = shoulder
    hx, hy = hip
    wx, wy = wrist

    # Torso flat: shoulder->hip line should be close to horizontal in SIDE view.
    # Compute angle to horizontal (0 deg = horizontal).
    dx = hx - sx
    dy = hy - sy
    torso_flat = math.degrees(math.atan2(abs(dy), abs(dx) + 1e-9))

    # Wrist under shoulder: x alignment in SIDE view.
    wrist_under_shoulder_dx = abs(wx - sx)

    # Hip should not sag too much relative to shoulder (close to 0).
    hip_drop = hy - sy

    return {
        "side": side,
        "torso_flat": torso_flat,
        "wrist_under_shoulder_dx": wrist_under_shoulder_dx,
        "hip_drop": hip_drop,
    }

def plank_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    torso_flat_max=20.0,            # deg away from horizontal
    wrist_under_shoulder_dx_max=0.15,  # normalized units
    hip_drop_abs_max=0.20,          # |hip.y - shoulder.y|
    # soft ranges for match index (how quickly score drops near threshold)
    torso_flat_soft=10.0,
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
        and m["wrist_under_shoulder_dx"] <= wrist_under_shoulder_dx_max
        and abs(m["hip_drop"]) <= hip_drop_abs_max
    )

    torso_score = score_below(m["torso_flat"], torso_flat_max, torso_flat_soft)
    wrist_score = score_below(m["wrist_under_shoulder_dx"], wrist_under_shoulder_dx_max, wrist_dx_soft)
    hip_score = score_below_abs(m["hip_drop"], hip_drop_abs_max, hip_drop_soft)

    match_index = 0.45 * torso_score + 0.35 * wrist_score + 0.20 * hip_score
    return (matched, match_index)
