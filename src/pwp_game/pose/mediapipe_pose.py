import time
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp


@dataclass
class PoseResult:
    landmarks: Optional[object]
    timestamp: float


class PoseEstimator:
    def __init__(
        self,
        model_complexity: int = 1,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ) -> None:
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame) -> PoseResult:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb)
        return PoseResult(landmarks=results.pose_landmarks, timestamp=time.time())

    def close(self) -> None:
        self._pose.close()
