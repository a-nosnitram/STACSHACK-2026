from dataclasses import dataclass, field


@dataclass
class CameraConfig:
    index: int
    width: int = 640
    height: int = 480
    fps: int = 30


@dataclass
class AppConfig:
    camera0: CameraConfig = field(default_factory=lambda: CameraConfig(0))
    camera1: CameraConfig = field(default_factory=lambda: CameraConfig(1))
    pose_model_complexity: int = 1
    detection_confidence: float = 0.5
    tracking_confidence: float = 0.5
    ui_fps: int = 30
