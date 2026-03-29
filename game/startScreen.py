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
    font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 28)

    running = True
    clock = pygame.time.Clock()
    while running:
        screen.blit(background, (0, 0))

        logo = pygame.image.load("assets/logo/logo1-bg.png").convert_alpha()
        # scale to preserve aspect ratio and fit within a 600x600 box
        logo_width, logo_height = logo.get_size()
        scale_factor = min(600 / logo_width, 600 / logo_height)
        logo = pygame.transform.scale(
            logo, (int(logo_width * scale_factor), int(logo_height * scale_factor)))
        screen.blit(logo, logo.get_rect(center=(screen_width // 2, 200)))

        # Prompt
        text = font.render("PRESS ANY BUTTON TO CONTINUE",
                           True, (255, 255, 255))
        screen.blit(text, text.get_rect(
            center=(screen_width // 2, screen_height - 80)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return []
            if event.type == pygame.KEYDOWN:
                running = False
        pygame.display.flip()
        clock.tick(60)
