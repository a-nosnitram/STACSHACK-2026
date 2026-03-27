from typing import Tuple

from .camera_stream import CameraStream


class MultiCameraManager:
    def __init__(self, cam0: CameraStream, cam1: CameraStream) -> None:
        self.cam0 = cam0
        self.cam1 = cam1

    def open(self) -> None:
        self.cam0.open()
        self.cam1.open()

    def read(self) -> Tuple[bool, object, bool, object]:
        ok0, frame0 = self.cam0.read()
        ok1, frame1 = self.cam1.read()
        return ok0, frame0, ok1, frame1

    def close(self) -> None:
        self.cam0.close()
        self.cam1.close()
