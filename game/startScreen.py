from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable, List
import pygame


def run_start_screen(screen: pygame.Surface, background):
    if not pygame.get_init():
        pygame.init()
    font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 28)
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.blit(background, (0, 0))
        text = font.render("PRESS ANY BUTTON TO CONTINUE", True, (255, 255, 255))
        screen.blit(text, (400, 600))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return []
            if event.type == pygame.KEYDOWN:
                running = False
        pygame.display.flip()
        clock.tick(60)