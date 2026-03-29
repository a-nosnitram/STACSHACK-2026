from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import pygame


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
POSES_IMAGE_DIR = PROJECT_DIR / "assets" / "poses"
FONT_PATH = PROJECT_DIR / "assets" / "fonts" / "Silkscreen-Regular.ttf"


def load_pose_names(path: str | Path) -> List[str]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return sorted(data.keys())


def load_pose_image(pose_name: str, size: tuple[int, int]) -> pygame.Surface:
    image_path = POSES_IMAGE_DIR / f"{pose_name}.png"

    if image_path.exists():
        image = pygame.image.load(str(image_path)).convert_alpha()
        return pygame.transform.scale(image, size)

    placeholder = pygame.Surface(size, pygame.SRCALPHA)
    placeholder.fill((70, 70, 80))
    pygame.draw.rect(placeholder, (180, 180, 180), placeholder.get_rect(), 2)
    return placeholder


def run_pose_menu(
    screen: pygame.Surface,
    pose_names: Iterable[str],
    background,
    max_select: int = 5,
    title: str = "SELECT UP TO 5 POSES",
) -> List[str]:
    if not pygame.get_init():
        pygame.init()

    title_font = pygame.font.Font(str(FONT_PATH), 28)
    label_font = pygame.font.Font(str(FONT_PATH), 18)
    small_font = pygame.font.Font(str(FONT_PATH), 14)

    pose_list = list(pose_names)
    if not pose_list:
        return []

    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()

    selected: set[str] = set()
    cursor = 0

    cols = 3
    card_width = 220
    card_height = 180
    image_size = (120, 120)
    gap_x = 30
    gap_y = 24

    grid_width = cols * card_width + (cols - 1) * gap_x
    grid_start_x = (screen_width - grid_width) // 2
    grid_start_y = 140

    back_button = pygame.Rect(30, 25, 120, 42)
    start_button = pygame.Rect(screen_width // 2 - 110, screen_height - 70, 220, 44)

    pose_images = {
        pose_name: load_pose_image(pose_name, image_size)
        for pose_name in pose_list
    }

    def get_card_rect(index: int) -> pygame.Rect:
        row = index // cols
        col = index % cols
        x = grid_start_x + col * (card_width + gap_x)
        y = grid_start_y + row * (card_height + gap_y)
        return pygame.Rect(x, y, card_width, card_height)

    def draw_button(rect: pygame.Rect, text: str, mouse_pos, enabled=True):
        if not enabled:
            fill = (50, 50, 50)
            border = (120, 120, 120)
            text_color = (150, 150, 150)
        else:
            fill = (95, 95, 95) if rect.collidepoint(mouse_pos) else (40, 40, 40)
            border = (255, 255, 255)
            text_color = (255, 255, 255)

        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

        text_surface = label_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    while True:
        screen.blit(background, (0, 0))

        title_surf = title_font.render(title, True, (240, 240, 240))
        screen.blit(title_surf, title_surf.get_rect(center=(screen_width // 2, 35)))

        hint_text = "ARROWS/WASD MOVE   SPACE/CLICK SELECT   ENTER OR START TO CONFIRM"
        hint_surf = small_font.render(hint_text, True, (180, 180, 180))
        screen.blit(hint_surf, hint_surf.get_rect(center=(screen_width // 2, 72)))

        count_text = f"SELECTED: {len(selected)}/{max_select}"
        count_surf = label_font.render(count_text, True, (200, 200, 240))
        screen.blit(count_surf, count_surf.get_rect(center=(screen_width // 2, 102)))

        mouse_pos = pygame.mouse.get_pos()

        for i, pose_name in enumerate(pose_list):
            rect = get_card_rect(i)
            hovered = rect.collidepoint(mouse_pos)
            focused = i == cursor
            is_selected = pose_name in selected

            fill_color = (55, 55, 65)
            if hovered:
                fill_color = (75, 75, 90)

            border_color = (255, 255, 255)
            if focused:
                border_color = (255, 215, 100)
            if is_selected:
                border_color = (100, 255, 140)

            pygame.draw.rect(screen, fill_color, rect, border_radius=10)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)

            image = pose_images[pose_name]
            image_rect = image.get_rect(center=(rect.centerx, rect.y + 70))
            screen.blit(image, image_rect)

            name_surf = label_font.render(pose_name.upper(), True, (230, 230, 230))
            name_rect = name_surf.get_rect(center=(rect.centerx, rect.bottom - 28))
            screen.blit(name_surf, name_rect)

            mark = "[X]" if is_selected else "[ ]"
            mark_surf = small_font.render(mark, True, border_color)
            screen.blit(mark_surf, (rect.x + 10, rect.y + 10))

        draw_button(back_button, "BACK", mouse_pos, enabled=True)
        draw_button(start_button, "START", mouse_pos, enabled=len(selected) > 0)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return []

            if event.type == pygame.KEYDOWN:
                row = cursor // cols
                col = cursor % cols

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if col > 0:
                        cursor -= 1

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if col < cols - 1 and cursor + 1 < len(pose_list):
                        cursor += 1

                elif event.key in (pygame.K_UP, pygame.K_w):
                    if row > 0:
                        cursor -= cols

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if cursor + cols < len(pose_list):
                        cursor += cols

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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    return []

                if start_button.collidepoint(event.pos) and selected:
                    return list(selected)

                for i, pose_name in enumerate(pose_list):
                    rect = get_card_rect(i)
                    if rect.collidepoint(event.pos):
                        cursor = i
                        if pose_name in selected:
                            selected.remove(pose_name)
                        else:
                            if len(selected) < max_select:
                                selected.add(pose_name)

    return list(selected)