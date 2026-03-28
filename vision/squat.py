"""
Side-squat detector using angles + a torso (shoulder-hip) constraint.

Input expects normalized landmarks (translation+scale normalized) where each landmark has:
  - x, y (and optionally z)
  - presence (recommended)

Best with a SIDE camera view.
"""

import math

# MediaPipe indices
LS, RS = 11, 12
LH, RH = 23, 24
LK, RK = 25, 26
LA, RA = 27, 28


def get(lms, i):
    return lms[i]


def xy(lm):
    return float(lm.x), float(lm.y)


def presence(lm):
    return float(getattr(lm, "presence", 1.0))


def angle_deg(a, b, c):
    """Angle ABC in degrees using 2D points a,b,c = (x,y)."""
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


def choose_side(lms, *, p_min=0.5):
    """
    Choose left or right leg based on presence of (hip,knee,ankle).
    Returns "L", "R", or None.
    """
    left_ok = presence(get(lms, LH)) >= p_min and presence(get(lms, LK)) >= p_min and presence(get(lms, LA)) >= p_min
    right_ok = presence(get(lms, RH)) >= p_min and presence(get(lms, RK)) >= p_min and presence(get(lms, RA)) >= p_min

    if not left_ok and not right_ok:
        return None
    if left_ok and not right_ok:
        return "L"
    if right_ok and not left_ok:
        return "R"

    left_score = presence(get(lms, LH)) + presence(get(lms, LK)) + presence(get(lms, LA))
    right_score = presence(get(lms, RH)) + presence(get(lms, RK)) + presence(get(lms, RA))
    return "L" if left_score >= right_score else "R"


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


def _score_below(value: float, limit: float, soft: float) -> float:
    """1.0 when value is <= limit-soft, 0.0 when value >= limit."""
    soft = max(1e-6, float(soft))
    return _clamp01((limit - value) / soft)


def _score_above(value: float, limit: float, soft: float) -> float:
    """1.0 when value is >= limit+soft, 0.0 when value <= limit."""
    soft = max(1e-6, float(soft))
    return _clamp01((value - limit) / soft)

def squat_metrics(normalized_landmarks, *, p_min=0.5):
    """
    Returns metrics for the most reliable (visible) side:
      - knee_angle: angle(hip-knee-ankle)
      - hip_angle: angle(shoulder-hip-knee)
      - torso_lean: torso (hip->shoulder) lean relative to vertical (deg)
      - hip_drop: hip.y - shoulder.y (positive means hips lower than shoulders)
    """
    lms = normalized_landmarks
    side = choose_side(lms, p_min=p_min)
    if side is None:
        return None

    if side == "L":
        shoulder = xy(get(lms, LS))
        hip = xy(get(lms, LH))
        knee = xy(get(lms, LK))
        ankle = xy(get(lms, LA))
    else:
        shoulder = xy(get(lms, RS))
        hip = xy(get(lms, RH))
        knee = xy(get(lms, RK))
        ankle = xy(get(lms, RA))

    knee_angle = angle_deg(hip, knee, ankle)
    hip_angle =  angle_deg(shoulder, hip, knee)

    # Shoulder-hip (torso) constraint:
    # torso_lean = 0° upright, 90° horizontal. Helps reject plank-like / horizontal poses.
    hx, hy = hip
    sx, sy = shoulder
    dx = sx - hx
    dy = sy - hy
    torso_lean = math.degrees(math.atan2(abs(dx), abs(dy) + 1e-9))

    # In image coords, bigger y usually means "lower" on screen.
    hip_drop = hip[1] - shoulder[1]

    return {
        "side": side,
        "knee_angle": knee_angle,
        "hip_angle": hip_angle,
        "torso_lean": torso_lean,
        "hip_drop": hip_drop,
    }


def squat_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    knee_angle_max=120.0,
    hip_angle_max=130.0,
    hip_drop_min=0.15,
    torso_lean_max=70.0,
    # "Soft" scoring ranges (how quickly score drops near the threshold)
    knee_soft_deg=25.0,
    hip_soft_deg=25.0,
    torso_soft_deg=20.0,
    hip_drop_soft=0.10,
):
    """
    Returns (matched_bool, match_index_0_to_1).

    Constraints:
    - knee bend (knee_angle <= knee_angle_max)
    - hip bend (hip_angle <= hip_angle_max)
    - hips lowered (hip_drop >= hip_drop_min)
    - torso not too horizontal (torso_lean <= torso_lean_max)
    """
    m = squat_metrics(normalized_landmarks, p_min=p_min)
    if m is None:
        return (False, 0.0)

    matched = (
        m["knee_angle"] <= knee_angle_max
        and m["hip_angle"] <= hip_angle_max
        and m["hip_drop"] >= hip_drop_min
        and m["torso_lean"] <= torso_lean_max
    )

    # Smooth 0..1 "matching index" for UI/mana meters.
    knee_score = _score_below(m["knee_angle"], knee_angle_max, knee_soft_deg)
    hip_score = _score_below(m["hip_angle"], hip_angle_max, hip_soft_deg)
    torso_score = _score_below(m["torso_lean"], torso_lean_max, torso_soft_deg)
    drop_score = _score_above(m["hip_drop"], hip_drop_min, hip_drop_soft)

    # Weighted average (emphasize knee + hip).
    match_index = (0.35 * knee_score + 0.35 * hip_score + 0.2 * drop_score + 0.1 * torso_score)

    return (matched, match_index)
