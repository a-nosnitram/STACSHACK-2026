# vision/pose_recognition.py

import json
import math
from pathlib import Path
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

    left_score = presence(get(lms, LH)) + presence(get(lms, LK)) + presence(get(lms, LA))
    right_score = presence(get(lms, RH)) + presence(get(lms, RK)) + presence(get(lms, RA))
    return "L" if left_score >= right_score else "R"




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
        pose_name: str,
        live_person_landmarks,
) -> None | dict:
    if pose_name == "squat":
        return squat_match(live_person_landmarks)
    return None





def _cosine_dist(a: list[float], b: list[float]) -> float:
    """Cosine distance (lower is more similar)."""
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    return float(1.0 - (np.dot(va, vb) / ((np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9)))


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
