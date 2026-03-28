import math

# MediaPipe pose landmark indices
LS, RS = 11, 12  # shoulders
LE, RE = 13, 14  # elbows
LW, RW = 15, 16  # wrists
LH, RH = 23, 24  # hips
LK, RK = 25, 26  # knees
LA, RA = 27, 28  # ankles
LHEEL, RHEEL = 29, 30  # heels
LFOOT, RFOOT = 31, 32  # foot index (toes)


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


def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


def score_below(value: float, limit: float, soft: float) -> float:
    """1.0 when value is <= limit-soft, 0.0 when value >= limit."""
    soft = max(1e-6, float(soft))
    return clamp01((limit - value) / soft)


def score_above(value: float, limit: float, soft: float) -> float:
    """1.0 when value is >= limit+soft, 0.0 when value <= limit."""
    soft = max(1e-6, float(soft))
    return clamp01((value - limit) / soft)


def score_below_abs(value: float, limit: float, soft: float) -> float:
    return score_below(abs(value), limit, soft)
