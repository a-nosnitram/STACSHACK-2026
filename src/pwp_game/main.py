import argparse
import time

from .config import AppConfig, CameraConfig
from .camera.camera_stream import CameraStream
from .camera.multi_camera import MultiCameraManager
from .pose.mediapipe_pose import PoseEstimator
from .pose.pose_classifier import PoseClassifier
from .game.engine import GameEngine
from .ui.pygame_ui import PygameUI
from .utils.logging import setup_logging


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PWP pose fighting game")
    parser.add_argument("--camera0", type=int, default=0, help="Index for player 1 camera")
    parser.add_argument("--camera1", type=int, default=1, help="Index for player 2 camera")
    parser.add_argument("--dry-run", action="store_true", help="Run loop without camera or UI")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    setup_logging()

    config = AppConfig(
        camera0=CameraConfig(index=args.camera0),
        camera1=CameraConfig(index=args.camera1),
    )

    if args.dry_run:
        print("Dry run OK. Wiring complete.")
        return

    cam0 = CameraStream(**config.camera0.__dict__)
    cam1 = CameraStream(**config.camera1.__dict__)
    cams = MultiCameraManager(cam0, cam1)

    pose_estimator = PoseEstimator(
        model_complexity=config.pose_model_complexity,
        detection_confidence=config.detection_confidence,
        tracking_confidence=config.tracking_confidence,
    )
    classifier = PoseClassifier()
    engine = GameEngine()
    ui = PygameUI(target_fps=config.ui_fps)

    cams.open()
    ui.open()

    try:
        last_tick = time.time()
        while ui.is_running:
            ok0, frame0, ok1, frame1 = cams.read()
            if not ok0 or not ok1:
                continue

            pose0 = pose_estimator.process(frame0)
            pose1 = pose_estimator.process(frame1)

            pose_name0 = classifier.classify(pose0)
            pose_name1 = classifier.classify(pose1)

            engine.apply_pose(player_id=0, pose_name=pose_name0)
            engine.apply_pose(player_id=1, pose_name=pose_name1)

            ui.handle_events()
            ui.render(engine.state)

            now = time.time()
            if now - last_tick < 1.0 / config.ui_fps:
                time.sleep(max(0.0, (1.0 / config.ui_fps) - (now - last_tick)))
            last_tick = now
    finally:
        cams.close()
        ui.close()
