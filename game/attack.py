from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import pygame


_FIREBALL_CACHE: Dict[Tuple[int, bool], List[pygame.Surface]] = {}


def _load_fireball_frames(scale: int = 6, flipped: bool = False) -> List[pygame.Surface]:
    key = (scale, flipped)
    if key in _FIREBALL_CACHE:
        return _FIREBALL_CACHE[key]

    base_dir = Path(__file__).resolve().parent.parent / \
        "assets" / "effects" / "fireball"
    frames: List[pygame.Surface] = []
    for i in range(1, 5):
        path = base_dir / f"{i}.bmp"
        frame = pygame.image.load(str(path)).convert_alpha()
        frame = pygame.transform.scale(
            frame, (frame.get_width() * scale, frame.get_height() * scale)
        )
        if flipped:
            frame = pygame.transform.flip(frame, True, False)
        frames.append(frame)

    _FIREBALL_CACHE[key] = frames
    return frames


@dataclass
class Fireball:
    x: float
    y: float
    target_x: float
    direction: int
    speed: float = 12.0
    frame_interval: int = 4
    scale: int = 6

    _frame_idx: int = 0
    _frame_tick: int = 0
    _frames: List[pygame.Surface] = None
    active: bool = True

    def __post_init__(self) -> None:
        flipped = self.direction < 0
        self._frames = _load_fireball_frames(scale=self.scale, flipped=flipped)

    def update(self) -> None:
        if not self.active:
            return
        self.x += self.speed * self.direction
        self._frame_tick += 1
        if self._frame_tick >= self.frame_interval:
            self._frame_tick = 0
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)

        if self.direction > 0 and self.x >= self.target_x:
            self.active = False
        if self.direction < 0 and self.x <= self.target_x:
            self.active = False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.active:
            return
        frame = self._frames[self._frame_idx]
        screen.blit(frame, (int(self.x), int(self.y)))
