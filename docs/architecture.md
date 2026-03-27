# Architecture Notes

Data flow
- Two cameras feed frames to the laptop.
- MediaPipe extracts pose landmarks per player.
- Pose classifier maps landmarks to pose names.
- Game engine converts poses to attacks and updates state.
- UI renders health and basic feedback.

Key modules
- `camera/` handles capture and sync.
- `pose/` handles MediaPipe and classification.
- `game/` holds state and attack rules.
- `ui/` renders output.
