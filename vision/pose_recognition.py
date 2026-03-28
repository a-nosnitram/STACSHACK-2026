# vision/pose_recognition.py

import json
import math
from pathlib import Path

import numpy as np

LS, RS = 11, 12  # shoulders
LE, RE = 13, 14  # elbows
LW, RW = 15, 16  # wrists
LH, RH = 23, 24  # hips
LK, RK = 25, 26  # knees
LA, RA = 27, 28  # ankles

LANDMARK_NAMES = [
    "nose",
    "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear",
    "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_pinky", "right_pinky",
    "left_index", "right_index",
    "left_thumb", "right_thumb",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]



def load_poses(path: str | Path) -> dict:
    """Load pose templates from JSON. Returns {} if file doesn't exist."""
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def save_poses(db: dict, path: str | Path) -> None:
    """Save pose templates to JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(db, indent=2, sort_keys=True), encoding="utf-8")


def add_sample(db: dict, pose_name: str, features: list[float]) -> int:
    """Append one captured sample for a pose label. Returns new sample count."""
    db.setdefault(pose_name, []).append([float(x) for x in features])
    return len(db[pose_name])


# def capture_pose(result, db: dict, pose_name: str, *, path: str | Path, person_index: int = 0) -> bool:
#     """
#     Capture ONE pose sample and add to db under `pose_name`. Uses `person_index` to select which person 
#     - Returns True if captured, False if no person / low-confidence landmarks
#     """

#     # for safety, we check that the expected landmarks are present before trying to extract features.
#     # pose_lists = getattr(result, "pose_landmarks", None)
#     # if not pose_lists or len(pose_lists) <= person_index:
#     #     print("No pose detected.")
#     #     return False

#     # features = extract_features(pose_lists[person_index])
#     # if features is None:
#     #     print("Low confidence / degenerate pose; not captured.")
#     #     return False

#     pose_landmarks = result.pose_landmarks[person_index]  # for MediaPipe Tasks, this is already a list of 33 landmarks
#     if not pose_landmarks or len(pose_landmarks) < 33:
#         print("No pose detected.")
#         return False
    
#     features = extract_features(pose_landmarks)
#     if features is None:
#         print("Low confidence / degenerate pose; not captured.")
#         return False
    
#     for f in features:
#         print(f"{f:.3f}", end=" ")
#     print()

#     add_sample(db, pose_name, features)
#     save_poses(db, path)
#     return True


# def _pt(lm) -> np.ndarray:
#     """Landmark -> np.array([x,y])."""
#     return np.array([float(lm.x), float(lm.y)], dtype=np.float32)


# def _conf(lm, name: str, default: float = 1.0) -> float:
#     """Read lm.presence / lm.visibility if present; else default."""
#     return float(getattr(lm, name, default))


# def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
#     """Angle ABC in degrees for 2D points."""
#     ba, bc = a - b, c - b
#     denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-9
#     cosv = float(np.clip(np.dot(ba, bc) / denom, -1.0, 1.0))
#     return math.degrees(math.acos(cosv))


# def extract_features(person_landmark_list, *, min_presence: float = 0.5, min_visibility: float = 0.5) -> list[float] | None:
#     """
#     Convert ONE person's landmarks to a normalized feature vector.

#     Input: `person_landmark_list` = result.pose_landmarks[0]
#            (a landmark-list object with `.landmark` containing 33 landmarks)

#     Steps:
#     - Gate on landmark confidence for key joints (presence/visibility)
#     - Normalize:
#         origin = hip midpoint (removes translation)
#         scale  = shoulder width (removes distance-to-camera)
#     - Features (pose geometry):
#         elbow angles (L/R), shoulder angles (L/R),
#         wrist-to-wrist distance,
#         wrist vertical offsets vs shoulders (L/R),
#         knee-to-knee distance,
#         knee vertical offsets vs hip midpoint (L/R)

#     Returns: list[float] or None if low confidence / degenerate frame.
#     """
#     # MediaPipe Tasks: person_landmark_list is already a list of 33 landmarks.
#     # MediaPipe Solutions: person_landmark_list may have a `.landmark` list.
#     lms = getattr(person_landmark_list, "landmark", None)
#     if lms is None:
#         lms = person_landmark_list
#     if not lms or len(lms) < 33:
#         return None

#     key = [LS, RS, LH, RH, LK, RK]
#     for i in key:
#         if _conf(lms[i], "presence", 1.0) < min_presence:
#             return None
#         if _conf(lms[i], "visibility", 1.0) < min_visibility:
#             return None

#     ls, rs, le, re, lw, rw, lh, rh, lk, rk = map(
#         _pt,
#         [lms[LS], lms[RS], lms[LE], lms[RE], lms[LW], lms[RW], lms[LH], lms[RH], lms[LK], lms[RK]],
#     )

#     origin = (lh + rh) / 2.0
#     scale = float(np.linalg.norm(rs - ls))  # shoulder width
#     if scale < 1e-6:
#         return None

#     # Normalize (translation + scale)
#     ls, rs, le, re, lw, rw, lk, rk = [(p - origin) / scale for p in (ls, rs, le, re, lw, rw, lk, rk)]
#     o = np.array([0.0, 0.0], dtype=np.float32)

#     # Angles normalized roughly to 0..1 by /180
#     left_elbow = _angle(ls, le, lw) / 180.0
#     right_elbow = _angle(rs, re, rw) / 180.0
#     left_shoulder = _angle(o, ls, le) / 180.0
#     right_shoulder = _angle(o, rs, re) / 180.0

#     wrists_dist = float(np.linalg.norm(lw - rw))
#     lw_dy = float(lw[1] - ls[1])  # wrist relative to shoulder (y)
#     rw_dy = float(rw[1] - rs[1])

#     knees_dist = float(np.linalg.norm(lk - rk))
#     lk_dy = float(lk[1])  # knee relative to hip midpoint (origin is hip midpoint)
#     rk_dy = float(rk[1])

#     return [
#         left_elbow,
#         right_elbow,
#         left_shoulder,
#         right_shoulder,
#         wrists_dist,
#         lw_dy,
#         rw_dy,
#         knees_dist,
#         lk_dy,
#         rk_dy,
#     ]



def add_template(db: dict, pose_name: str, template: dict) -> int:
    """
    Store a captured pose template under `pose_name`.

    Template format:
      {
        "points": [[x,y,z], ...]  # 33 normalized landmarks
        "presence": [..],         # 33 floats
        "visibility": [..],       # 33 floats
      }
    """
    db.setdefault(pose_name, []).append(template)
    return len(db[pose_name])


def _pt3(lm) -> np.ndarray:
    return np.array([float(lm.x), float(lm.y), float(getattr(lm, "z", 0.0))], dtype=np.float32)


def extract_template(person_landmark_list) -> dict | None:
    """
    Normalize ALL 33 landmarks and keep per-landmark confidence.

    Normalization:
      origin = hip midpoint (translation)
      scale  = shoulder width in x/y (scale)
      z is also scaled by the same factor (works well enough for MVP).
    """
    lms = getattr(person_landmark_list, "landmark", None)
    if lms is None:
        lms = person_landmark_list
    if not lms or len(lms) < 33:
        return None

    pts = np.stack([_pt3(lm) for lm in lms[:33]], axis=0)  # (33,3)
    hip_mid = (pts[LH] + pts[RH]) / 2.0
    shoulder_width = float(np.linalg.norm((pts[RS] - pts[LS])[:2]))
    if shoulder_width < 1e-6:
        return None

    pts_n = (pts - hip_mid) / (shoulder_width + 1e-9)
    presence = [float(getattr(lm, "presence", 1.0)) for lm in lms[:33]]
    visibility = [float(getattr(lm, "visibility", 1.0)) for lm in lms[:33]]

    return {"points": pts_n.astype(float).tolist(), "presence": presence, "visibility": visibility}


def capture_pose_template(result, db: dict, pose_name: str, *, path: str | Path, person_index: int = 0) -> bool:
    """
    Capture ONE template sample (all 33 normalized landmarks + confidence) and save to JSON.
    """
    # pose_lists = getattr(result, "pose_landmarks", None)
    # if not pose_lists or len(pose_lists) <= person_index:
    #     return False

    pose_landmarks = result.pose_landmarks[person_index]  # for MediaPipe Tasks, this is already a list of 33 landmarks
    if not pose_landmarks or len(pose_landmarks) < 33:
        return False

    features = extract_template(pose_landmarks)
    if features is None:
        return False

    add_template(db, pose_name, features)
    save_poses(db, path)
    return True


def match_expected_pose(
    db: dict,
    pose_name: str,
    live_person_landmarks,
    *,
    p_min: float = 0.7,
    v_min: float = 0.7,
    min_points: int = 15,
    critical_sets: list[set[int]] | None = None,
    use_z: bool = True,
) -> tuple[float, int] | None:
    """
    Match live pose to expected template.

    Rules:
    - Only compare landmarks where live presence >= p_min (and visibility >= v_min if provided)
    - Require at least `min_points` usable landmarks
    - If `critical_sets` is provided, require at least one set to be fully usable

    Returns: (best_mean_distance, used_landmarks_count) or None.
    """
    templates = db.get(pose_name, [])
    if not templates:
        return None

    live = extract_template(live_person_landmarks)
    if live is None:
        return None

    live_pts = np.asarray(live["points"], dtype=np.float32)  # (33,3)
    live_presence = live["presence"]
    live_visibility = live["visibility"]

    usable: set[int] = set()
    for i in range(33):
        if live_presence[i] < p_min:
            continue
        if v_min is not None and live_visibility[i] < v_min:
            continue
        usable.add(i)

    if len(usable) < min_points:
        return None
    if critical_sets and not any(s.issubset(usable) for s in critical_sets):
        return None

    used = sorted(usable)
    dims = 3 if use_z else 2
    live_sel = live_pts[used, :dims]

    best = None
    for t in templates:
        if not isinstance(t, dict) or "points" not in t:
            continue
        t_pts = np.asarray(t["points"], dtype=np.float32)
        if t_pts.shape != (33, 3):
            continue
        t_sel = t_pts[used, :dims]
        d = float(np.mean(np.linalg.norm(live_sel - t_sel, axis=1)))
        if best is None or d < best:
            best = d

    if best is None:
        return None
    return best, len(used)


def squat_critical_sets() -> list[set[int]]:
    """Either left-side (hip,knee,ankle) or right-side must be usable."""
    return [{LH, LK, LA}, {RH, RK, RA}]


def plank_critical_sets() -> list[set[int]]:
    """Either left-side (shoulder,hip,ankle) or right-side must be usable."""
    return [{LS, LH, LA}, {RS, RH, RA}]


def _cosine_dist(a: list[float], b: list[float]) -> float:
    """Cosine distance (lower is more similar)."""
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    return float(1.0 - (np.dot(va, vb) / ((np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9)))


def best_match(db: dict, features: list[float]) -> tuple[str, float] | None:
    """
    Compare live `features` to all saved samples. Returns (pose_name, distance) or None.
    """
    best_name = None
    best_dist = None
    for name, samples in db.items():
        for sample in samples:
            if len(sample) != len(features):
                continue
            d = _cosine_dist(features, sample)
            if best_dist is None or d < best_dist:
                best_name, best_dist = name, d

    if best_name is None or best_dist is None:
        return None
    return best_name, float(best_dist)



def print_most_visible_landmarks(result, *, person_index=0, top_k=10, score="visibility"):
    """
    result: output of landmarker.detect_for_video(...)
    score: "visibility" or "presence"

    MediaPipe Tasks:
      result.pose_landmarks[person_index] is already a list of 33 landmarks.
    """
    pose_lists = getattr(result, "pose_landmarks", None)
    if not pose_lists or len(pose_lists) <= person_index:
        print("No person detected.")
        return

    lms = pose_lists[person_index]  # list of 33 landmarks
    scored = []
    for i, lm in enumerate(lms):
        s = getattr(lm, score, None)
        if s is None:
            continue
        name = LANDMARK_NAMES[i] if i < len(LANDMARK_NAMES) else f"landmark_{i}"
        scored.append((float(s), i, name))

    scored.sort(reverse=True)  # highest confidence first
    print(f"Top {top_k} by {score}:")
    for s, i, name in scored[:top_k]:
        presence = getattr(lms[i], "presence", None)
        visibility = getattr(lms[i], "visibility", None)
        print(
            f"{i:02d} {name:16s} {score}={s:.3f} "
            f"presence={(presence if presence is not None else float('nan')):.3f} "
            f"visibility={(visibility if visibility is not None else float('nan')):.3f}"
        )
