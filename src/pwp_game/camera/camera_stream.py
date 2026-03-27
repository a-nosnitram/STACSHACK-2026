from dataclasses import dataclass
from typing import Optional, Tuple

import cv2


@dataclass
class CameraStream:
    index: int
    width: int = 640
    height: int = 480
    fps: int = 30

    _cap: Optional[cv2.VideoCapture] = None

    def open(self) -> "CameraStream":
        cap = cv2.VideoCapture(self.index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not cap.isOpened():
            raise RuntimeError(f"Camera {self.index} failed to open")

        self._cap = cap
        return self

    def read(self) -> Tuple[bool, Optional[object]]:
        if self._cap is None:
            raise RuntimeError("Camera not opened")
        ok, frame = self._cap.read()
        return ok, frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
