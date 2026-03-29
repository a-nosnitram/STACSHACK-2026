from game.constants import poses as available_poses


def pose_combo(poses):
    if len(poses) == 5:
        return poses
    else:
        # fill the rest with repeated poses if there are not enough unique ones, to ensure we always send 5 poses to vision
        import random

        remaining_poses = [p for i in range(5 - len(poses)) for p in poses]
        random.shuffle(remaining_poses)
        return poses + remaining_poses[: (5 - len(poses))]
