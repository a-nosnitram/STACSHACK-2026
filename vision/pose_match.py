from vision.poses.bug import dead_bug_match
from vision.poses.plank import plank_match
from vision.poses.squat import squat_match

def match_expected_pose(
    pose_name: str,
    live_person_landmarks,
) -> None | dict:
    if pose_name == "squat":
        return squat_match(live_person_landmarks)
    elif pose_name == "plank":
        return plank_match(live_person_landmarks)
    elif pose_name == "bug":
        return dead_bug_match(live_person_landmarks)
    return None
