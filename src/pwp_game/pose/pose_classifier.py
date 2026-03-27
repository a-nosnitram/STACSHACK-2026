from typing import Iterable, Optional

from .mediapipe_pose import PoseResult
from .pose_defs import DEFAULT_POSES, PoseName, PoseDefinition


class PoseClassifier:
    def __init__(self, pose_defs: Optional[Iterable[PoseDefinition]] = None) -> None:
        self.pose_defs = list(pose_defs) if pose_defs is not None else list(DEFAULT_POSES)

    def classify(self, pose: PoseResult) -> PoseName:
        if pose.landmarks is None:
            return PoseName.IDLE

        # TODO: Replace with real feature extraction and matching.
        return PoseName.UNKNOWN
