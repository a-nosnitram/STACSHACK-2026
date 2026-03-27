# PWP Game (Python)

Two player pose fighting game. Two cameras feed MediaPipe pose data to the laptop. Each pose maps to an attack. This repo is a starter scaffold for the MVP.

MVP goals
- Get two cameras to communicate with the laptop and send pose data.
- Pose recognition.
- Simple offensive attacks.
- Static preset poses to attacks.
- Basic UI.

Project layout
- `src/pwp_game/`: core package.
- `src/pwp_game/camera/`: camera capture and sync.
- `src/pwp_game/pose/`: MediaPipe integration and pose classification.
- `src/pwp_game/game/`: game rules and state.
- `src/pwp_game/ui/`: basic UI.
- `tests/`: test stubs.
- `assets/`: UI assets.
- `data/poses/`: reference pose data.
- `docs/`: notes and architecture.

Quickstart
1. Create a venv and install deps.
2. Run `pip install -r requirements.txt`.
3. Run `PYTHONPATH=src python -m pwp_game --camera0 0 --camera1 1`.
4. Use `--dry-run` to verify wiring without cameras or UI.

Notes
- This is a scaffold. The pose classifier and attacks are placeholders.
- MediaPipe and OpenCV must be installed for camera and pose capture.
