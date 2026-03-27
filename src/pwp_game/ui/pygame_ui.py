from typing import Optional

import pygame

from ..game.state import GameState


class PygameUI:
    def __init__(self, target_fps: int = 30, width: int = 960, height: int = 540) -> None:
        self.target_fps = target_fps
        self.width = width
        self.height = height
        self.is_running = False
        self._screen: Optional[pygame.Surface] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._font: Optional[pygame.font.Font] = None

    def open(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PWP Game")
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("Arial", 24)
        self.is_running = True

    def close(self) -> None:
        pygame.quit()
        self.is_running = False

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def render(self, state: GameState) -> None:
        if self._screen is None:
            return
        self._screen.fill((20, 20, 24))

        p0 = state.players[0].health
        p1 = state.players[1].health

        self._draw_health_bar(50, 40, p0, label="Player 1")
        self._draw_health_bar(self.width - 350, 40, p1, label="Player 2")

        pygame.display.flip()
        if self._clock is not None:
            self._clock.tick(self.target_fps)

    def _draw_health_bar(self, x: int, y: int, health: int, label: str) -> None:
        if self._screen is None:
            return
        bar_w = 300
        bar_h = 24
        fill_w = int(bar_w * max(0, min(health, 100)) / 100)

        pygame.draw.rect(self._screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h))
        pygame.draw.rect(self._screen, (200, 60, 60), pygame.Rect(x, y, fill_w, bar_h))
        pygame.draw.rect(self._screen, (240, 240, 240), pygame.Rect(x, y, bar_w, bar_h), 2)

        if self._font is not None:
            text = self._font.render(f"{label}: {health}", True, (230, 230, 230))
            self._screen.blit(text, (x, y - 26))
