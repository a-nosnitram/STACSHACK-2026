from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import pygame


def load_pose_names(path: str | Path) -> List[str]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    data = json.loads(file_path.read_text())
    return sorted(data.keys())


def run_pose_menu(
    screen: pygame.Surface,
    pose_names: Iterable[str],
    max_select: int = 5,
    title: str = "Select up to 5 poses",
) -> List[str]:
    if not pygame.get_init():
        pygame.init()

    font = pygame.font.SysFont("Arial", 28)
    small = pygame.font.SysFont("Arial", 20)

    pose_list = list(pose_names)
    if not pose_list:
        return []

    selected: set[str] = set()
    cursor = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill((14, 14, 18))

        title_surf = font.render(title, True, (240, 240, 240))
        screen.blit(title_surf, (40, 30))

        hint_text = "Arrows/W-S move | Space toggles | Enter confirms | Esc cancels"
        hint_surf = small.render(hint_text, True, (180, 180, 180))
        screen.blit(hint_surf, (40, 70))

        count_text = f"Selected: {len(selected)}/{max_select}"
        count_surf = small.render(count_text, True, (200, 200, 240))
        screen.blit(count_surf, (40, 95))

        visible_rows = 12
        max_start = max(0, len(pose_list) - visible_rows)
        start = min(max(0, cursor - visible_rows // 2), max_start)
        end = min(len(pose_list), start + visible_rows)

        y = 140
        for idx in range(start, end):
            pose = pose_list[idx]
            is_selected = pose in selected
            prefix = "[x]" if is_selected else "[ ]"
            color = (255, 215, 100) if idx == cursor else (220, 220, 220)
            line = f"{prefix} {pose}"
            line_surf = font.render(line, True, color)
            screen.blit(line_surf, (60, y))
            y += 36

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return []
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    cursor = (cursor - 1) % len(pose_list)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    cursor = (cursor + 1) % len(pose_list)
                elif event.key == pygame.K_SPACE:
                    pose = pose_list[cursor]
                    if pose in selected:
                        selected.remove(pose)
                    else:
                        if len(selected) < max_select:
                            selected.add(pose)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected:
                        return list(selected)
                elif event.key == pygame.K_ESCAPE:
                    return []

    return list(selected)
