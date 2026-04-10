# SuperPosition — STACS Hack 2026 Winner

**SuperPosition** is a two‑player, pose‑powered PvP game that turns physiotherapy exercises into a competitive and social game. It is built around a live CV-to-game loop using MediaPipe.

## Pitch (Context)
**Problem**
- Physiotherapy can feel lonely, difficult, and intimidating.
- Long waitlists delay treatment and motivation often drops early.

**Solution**
- **Gamified rehabilitation**: turn exercises into a competitive, social experience.
- Players battle by doing rehab poses with better form.

**What It Is**
- Players compete head‑to‑head.
- If you perform a pose with better form than your opponent, your avatar **throws a fireball**.

## What It Does
- Players select up to 5 physio poses for a set (e.g., squat, plank, lunge, dead‑bug).
- The game sends that pose list to vision.
- Vision scores each player’s form by **joint‑angle correctness**.
- The round winner triggers an in‑game attack.

## How It Works (High Level)
1. **Phones** stream camera frames to the laptop over websockets.
2. **Vision** (MediaPipe Pose Landmarker) detects joints and scores pose quality.
3. **Game** consumes round results and triggers attacks + UI updates.

## Project Layout
```
assets/        Sprites, backgrounds, pose images, fonts
game/          Pygame UI, menus, combat logic
vision/        MediaPipe pose detection + scoring
phone_cam/     Websocket receiver for phone video frames
shared/        Async queues for game <-> vision
models/        MediaPipe pose model (.task)
index.html     Phone camera web client
config.js      Phone client websocket URL
main.py        Runs server + vision + game together
```

## Requirements
- **Python 3.12 or 3.13** (3.14 is not supported by NumPy/OpenCV/MediaPipe)
- **uv** for environment + deps
- MediaPipe Pose Landmarker `.task` model

## Setup
```bash
uv python install 3.12
uv python pin 3.12
uv sync
```

If you see reflink warnings on macOS, use:
```bash
export UV_LINK_MODE=copy
uv sync
```

## MediaPipe Model
Download a Pose Landmarker `.task` model and place it here:
```
models/pose_landmarker_heavy.task
```

## Run (Game + Vision + Server)
```bash
uv run python main.py
```
This starts:
- the websocket server for phone streams (`ws://<laptop-ip>:8765`),
- the vision loop, and
- the game UI.

## Phone Camera Setup (Web Client)
1. Edit `config.js`:
```
WS_URL: "ws://<laptop-ip>:8765"
```
If you need remote access, use ngrok and set `WS_URL` to the wss URL.

2. Serve the web client:
```bash
python -m http.server 8000
```

3. Open on each phone:
```
http://<laptop-ip>:8000
```
Each phone will connect and stream frames.

## Gameplay Flow
- Each round:
  - **Prep phase**: get into position
  - **Hold phase**: score snapshots taken each frame
- Scores are averaged over the hold phase.

## Troubleshooting
- **Pygame font/BMP issues**: ensure Python 3.12 and reinstall deps with `uv sync`.
- **OpenCV import errors**: rebuild the env or install missing system libs.
- **No model found**: confirm `models/pose_landmarker_heavy.task` exists.

---
Built at STACS Hack 2026 with MediaPipe, OpenCV, and Pygame.
