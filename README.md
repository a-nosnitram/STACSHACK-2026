# MVP Checklist

- [ ] Connect two cameras (phone streams) and confirm frames from each.
- [ ] Integrate MediaPipe pose extraction for both players.
- [ ] Define 3 to 5 static poses and map to attacks.
- [ ] Implement basic cooldowns and damage.
- [ ] Render health bars and pose labels.

## How to run camera

```sh
uv run python phone-cam/server.py # terminal 1
python -m http.server 8000 # terminal 2
```

Cuz eduoram doesn't work properly you connect to localhost through ngrok (it's running on my machine atm): `https://natasha-unannunciative-noninterdependently.ngrok-free.dev`

## If uv doesn't work
```sh
rm -rf .venv
uv python install 3.12
uv python pin 3.12
export UV_LINK_MODE=copy
uv sync
```
test
```sh
uv run python -c "import numpy, cv2, pygame; print('ok')"
```
then
```sh
uv run python main.py
```