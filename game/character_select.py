import json
from pathlib import Path
import pygame


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
CONFIG_PATH = PROJECT_DIR / "assets" / "configs" / "characters.json"


def load_characters():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["characters"]


def load_preview_image(path: str, size=(120, 120)):
    full_path = PROJECT_DIR / path
    image = pygame.image.load(str(full_path)).convert_alpha()
    return pygame.transform.scale(image, size)


def run_character_select(screen: pygame.Surface, background):
    if not pygame.get_init():
        pygame.init()

    clock = pygame.time.Clock()

    title_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 26)
    label_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 20)
    small_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 16)

    screen_width, screen_height = screen.get_size()

    characters = load_characters()
    if len(characters) < 4:
        raise ValueError("В characters.json должно быть минимум 4 персонажа")

    characters = characters[:4]

    previews = {}
    for char in characters:
        previews[char["id"]] = load_preview_image(char["preview"])

    selected_left = 0
    selected_right = 1

    left_panel = pygame.Rect(40, 90, screen_width //
                             2 - 60, screen_height - 180)
    right_panel = pygame.Rect(
        screen_width // 2 + 20, 90, screen_width // 2 - 60, screen_height - 180
    )

    back_button = pygame.Rect(30, 25, 120, 40)
    confirm_button = pygame.Rect(
        screen_width // 2 - 100, screen_height - 70, 200, 42)

    card_width = 170
    card_height = 180
    gap_x = 30
    gap_y = 30

    def make_card_rects(panel_rect):
        total_width = card_width * 2 + gap_x
        start_x = panel_rect.x + (panel_rect.width - total_width) // 2
        start_y = panel_rect.y + 70

        return [
            pygame.Rect(start_x, start_y, card_width, card_height),
            pygame.Rect(start_x + card_width + gap_x,
                        start_y, card_width, card_height),
            pygame.Rect(start_x, start_y + card_height +
                        gap_y, card_width, card_height),
            pygame.Rect(
                start_x + card_width + gap_x,
                start_y + card_height + gap_y,
                card_width,
                card_height,
            ),
        ]

    left_cards = make_card_rects(left_panel)
    right_cards = make_card_rects(right_panel)
    dark_overlay = pygame.Surface((screen_width, screen_height))
    dark_overlay.set_alpha(120)
    dark_overlay.fill((0, 0, 0))

    def draw_button(rect, text, mouse_pos):
        fill = (95, 95, 95) if rect.collidepoint(mouse_pos) else (40, 40, 40)
        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=8)

        text_surface = label_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def draw_card(rect, char_data, selected, hovered):
        fill = (75, 75, 75) if hovered else (45, 45, 45)
        border = (255, 220, 100) if selected else (255, 255, 255)

        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 3, border_radius=10)

        preview = previews[char_data["id"]]
        preview_rect = preview.get_rect(center=(rect.centerx, rect.y + 62))
        screen.blit(preview, preview_rect)

        name_text = label_font.render(
            char_data["name"].upper(), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(rect.centerx, rect.bottom - 30))
        screen.blit(name_text, name_rect)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        screen.blit(background, (0, 0))

        screen.blit(dark_overlay, (0, 0))

        pygame.draw.rect(screen, (25, 25, 25), left_panel, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255),
                         left_panel, 2, border_radius=12)

        pygame.draw.rect(screen, (25, 25, 25), right_panel, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255),
                         right_panel, 2, border_radius=12)

        title = title_font.render("CHOOSE CHARACTERS", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen_width // 2, 45)))

        left_label = label_font.render("PLAYER 1", True, (255, 255, 255))
        right_label = label_font.render("PLAYER 2", True, (255, 255, 255))

        screen.blit(left_label, left_label.get_rect(
            center=(left_panel.centerx, left_panel.y + 30)))
        screen.blit(right_label, right_label.get_rect(
            center=(right_panel.centerx, right_panel.y + 30)))

        help_text = small_font.render(
            "LEFT: WASD   RIGHT: ARROWS   ENTER: CONFIRM   ESC: BACK",
            True,
            (220, 220, 220),
        )
        screen.blit(help_text, help_text.get_rect(
            center=(screen_width // 2, screen_height - 625)))

        for i, rect in enumerate(left_cards):
            draw_card(
                rect,
                characters[i],
                selected=(i == selected_left),
                hovered=rect.collidepoint(mouse_pos),
            )

        for i, rect in enumerate(right_cards):
            draw_card(
                rect,
                characters[i],
                selected=(i == selected_right),
                hovered=rect.collidepoint(mouse_pos),
            )

        draw_button(back_button, "BACK", mouse_pos)
        draw_button(confirm_button, "CONFIRM", mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

                elif event.key == pygame.K_RETURN:
                    return {
                        "left": characters[selected_left]["id"],
                        "right": characters[selected_right]["id"],
                    }

                elif event.key == pygame.K_a:
                    if selected_left in (1, 3):
                        selected_left -= 1
                elif event.key == pygame.K_d:
                    if selected_left in (0, 2):
                        selected_left += 1
                elif event.key == pygame.K_w:
                    if selected_left in (2, 3):
                        selected_left -= 2
                elif event.key == pygame.K_s:
                    if selected_left in (0, 1):
                        selected_left += 2

                # PLAYER 2 (ARROWS)
                elif event.key == pygame.K_LEFT:
                    if selected_right in (1, 3):
                        selected_right -= 1
                elif event.key == pygame.K_RIGHT:
                    if selected_right in (0, 2):
                        selected_right += 1
                elif event.key == pygame.K_UP:
                    if selected_right in (2, 3):
                        selected_right -= 2
                elif event.key == pygame.K_DOWN:
                    if selected_right in (0, 1):
                        selected_right += 2

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    return None

                if confirm_button.collidepoint(event.pos):
                    return {
                        "left": characters[selected_left]["id"],
                        "right": characters[selected_right]["id"],
                    }

                for i, rect in enumerate(left_cards):
                    if rect.collidepoint(event.pos):
                        selected_left = i

                for i, rect in enumerate(right_cards):
                    if rect.collidepoint(event.pos):
                        selected_right = i

        pygame.display.flip()
        clock.tick(60)
