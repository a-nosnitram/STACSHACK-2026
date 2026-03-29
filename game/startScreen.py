from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable, List
import pygame


def run_start_screen(screen: pygame.Surface, background):
    if not pygame.get_init():
        pygame.init()
    pygame.font.init()

    screen_width, screen_height = screen.get_size()
    title_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 56)
    font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 28)

    running = True
    clock = pygame.time.Clock()
    while running:
        screen.blit(background, (0, 0))

        # Title (draw every frame so it isn't overwritten by the background blit)
        title = title_font.render("SUPERPOSITION", True, (245, 245, 250))
        # subtle shadow for readability
        shadow = title_font.render("SUPERPOSITION", True, (0, 0, 0))
        title_pos = (screen_width // 2, 220)
        screen.blit(shadow, shadow.get_rect(center=(title_pos[0] + 3, title_pos[1] + 3)))
        screen.blit(title, title.get_rect(center=title_pos))

        # Prompt
        text = font.render("PRESS ANY BUTTON TO CONTINUE", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height - 80)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return []
            if event.type == pygame.KEYDOWN:
                running = False
        pygame.display.flip()
        clock.tick(60)
