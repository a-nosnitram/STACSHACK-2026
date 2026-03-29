
def pose_combo(poses):
    if len(poses) == 5:
        return poses
    else:
        # fill the rest with random poses
        import random

        all_poses = [
            "squat",
            "lunge",
            "dead_bug",
            "kick",
            "dab",
            "dab_reverse",
            "tree",
            "warrior2_left",
            "warrior2_right",
        ]
        remaining_poses = [p for p in all_poses if p not in poses]
        random.shuffle(remaining_poses)
        return poses + remaining_poses[: (5 - len(poses))]
