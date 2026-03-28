from vision.plank import plank_match
from vision.squat import squat_match

def match_expected_pose(
    pose_name: str,
    live_person_landmarks,
) -> None | dict:
    if pose_name == "squat":
        return squat_match(live_person_landmarks)
    elif pose_name == "plank":
        return plank_match(live_person_landmarks)
    return None
