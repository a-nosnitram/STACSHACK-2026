# vision/poses/lunge.py
# Static lunge detector (side view).
#
# Checks (simple + robust):
# - one "front" knee ~ 90°
# - other "back" knee fairly straight
# - ankles NOT stacked (dx >= min) but also NOT extremely split (dx <= max)
# - front knee roughly over front ankle (loose)
#
# Returns: (matched_bool, match_index_0_to_1)

from __future__ import annotations

from vision.pose_utils import (
    LA,
    LH,
    LK,
    RA,
    RH,
    RK,
    angle_deg,
    get,
    presence,
    score_below,
    score_below_abs,
    xy,
)


def lunge_metrics(normalized_landmarks, *, p_min=0.5):
    lms = normalized_landmarks

    # Need both legs for a lunge check (hip+knee+ankle on both sides).
    need = [LH, LK, LA, RH, RK, RA]
    if any(presence(get(lms, i)) < p_min for i in need):
        return None

    lh, lk, la = map(lambda i: xy(get(lms, i)), [LH, LK, LA])
    rh, rk, ra = map(lambda i: xy(get(lms, i)), [RH, RK, RA])

    left_knee_angle = angle_deg(lh, lk, la)   # hip-knee-ankle
    right_knee_angle = angle_deg(rh, rk, ra)

    ankle_dx = abs(la[0] - ra[0])  # side-view "split" proxy along x

    left_stack_dx = abs(lk[0] - la[0])   # knee over ankle (for front leg)
    right_stack_dx = abs(rk[0] - ra[0])

    return {
        "left_knee_angle": left_knee_angle,
        "right_knee_angle": right_knee_angle,
        "ankle_dx": ankle_dx,
        "left_stack_dx": left_stack_dx,
        "right_stack_dx": right_stack_dx,
    }


def lunge_match(
    normalized_landmarks,
    *,
    p_min=0.5,
    # Front knee ~ 90
    front_knee_target=90.0,
    front_knee_err_max=25.0,
    # Back leg extended
    back_knee_min=160.0,
    # Ankle "not stacked but not huge split" band
    ankle_dx_min=0.12,
    ankle_dx_max=0.45,
    # Knee-over-ankle (front leg) constraint
    knee_over_ankle_dx_max=0.28,
    # soft ranges for match_index
    front_err_soft=15.0,
    back_soft=15.0,
    ankle_soft=0.08,
    stack_soft=0.12,
):
    """
    Returns (matched_bool, match_index_0_to_1).

    Evaluates both assignments:
      - front=left, back=right
      - front=right, back=left
    Returns the better-scoring one.
    """
    m = lunge_metrics(normalized_landmarks, p_min=p_min)
    if m is None:
        return (False, 0.0)

    def score_above(value: float, minimum: float, soft: float) -> float:
        # 1 if comfortably above minimum, 0 if at/below minimum.
        soft = max(1e-6, float(soft))
        if value >= minimum + soft:
            return 1.0
        if value <= minimum:
            return 0.0
        return float((value - minimum) / soft)

    def score_band(value: float, lo: float, hi: float, soft: float) -> float:
        # 1 if inside [lo, hi], smoothly drops to 0 outside by "soft".
        soft = max(1e-6, float(soft))
        if lo <= value <= hi:
            return 1.0
        if value < lo:
            return float(max(0.0, min(1.0, (value - (lo - soft)) / soft)))
        # value > hi
        return float(max(0.0, min(1.0, ((hi + soft) - value) / soft)))

    def eval_assignment(front_leg: str):
        if front_leg == "L":
            front_knee = m["left_knee_angle"]
            back_knee = m["right_knee_angle"]
            stack_dx = m["left_stack_dx"]
        else:
            front_knee = m["right_knee_angle"]
            back_knee = m["left_knee_angle"]
            stack_dx = m["right_stack_dx"]

        front_err = abs(front_knee - front_knee_target)

        matched = (
            front_err <= front_knee_err_max
            and back_knee >= back_knee_min
            and ankle_dx_min <= m["ankle_dx"] <= ankle_dx_max
            and stack_dx <= knee_over_ankle_dx_max
        )

        front_score = score_below_abs(front_err, front_knee_err_max, front_err_soft)
        back_score = score_above(back_knee, back_knee_min, back_soft)
        stance_score = score_band(m["ankle_dx"], ankle_dx_min, ankle_dx_max, ankle_soft)
        stack_score = score_below(stack_dx, knee_over_ankle_dx_max, stack_soft)

        match_index = (
            0.40 * front_score
            + 0.30 * back_score
            + 0.20 * stance_score
            + 0.10 * stack_score
        )
        return matched, float(match_index)

    out_L = eval_assignment("L")
    out_R = eval_assignment("R")
    return out_L if out_L[1] >= out_R[1] else out_R
