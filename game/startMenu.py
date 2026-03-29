import pygame


def run_start_menu(screen: pygame.Surface, background):
    if not pygame.get_init():
        pygame.init()
    pygame.font.init()

    clock = pygame.time.Clock()

    title_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 56)
    button_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 22)
    hint_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 16)

    screen_width, screen_height = screen.get_size()

    button_width = 240
    button_height = 50
    button_gap = 18

    start_y = 420  # leaves room for title

    start_button = pygame.Rect(
        (screen_width - button_width) // 2,
        start_y,
        button_width,
        button_height
    )

    character_button = pygame.Rect(
        (screen_width - button_width) // 2,
        start_y + button_height + button_gap,
        button_width,
        button_height
    )

    exit_button = pygame.Rect(
        (screen_width - button_width) // 2,
        start_y + 2 * (button_height + button_gap),
        button_width,
        button_height
    )

    buttons = [
        ("start", start_button, "START"),
        ("character", character_button, "CHARACTERS"),
        ("exit", exit_button, "EXIT"),
    ]
    cursor = 0

    def draw_shadow_rect(rect: pygame.Rect, *, radius: int = 12):
        shadow = pygame.Surface((rect.w + 12, rect.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow,
            (0, 0, 0, 110),
            pygame.Rect(6, 6, rect.w, rect.h),
            border_radius=radius,
        )
        screen.blit(shadow, (rect.x - 6, rect.y - 6))

    def draw_button(rect: pygame.Rect, label: str, *, hovered: bool, selected: bool):
        base = (35, 35, 42)
        hover = (55, 55, 66)
        border = (140, 140, 160)
        accent = (250, 210, 80)

        fill = hover if hovered else base
        if selected:
            fill = (45, 45, 55)
            border = accent

        draw_shadow_rect(rect, radius=12)
        pygame.draw.rect(screen, fill, rect, border_radius=12)
        pygame.draw.rect(screen, border, rect, 2, border_radius=12)

        # subtle top gloss
        gloss = pygame.Surface((rect.w, max(1, rect.h // 2)), pygame.SRCALPHA)
        pygame.draw.rect(
            gloss,
            (255, 255, 255, 22),
            pygame.Rect(0, 0, gloss.get_width(), gloss.get_height()),
            border_radius=12,
        )
        screen.blit(gloss, (rect.x, rect.y))

        text = button_font.render(label, True, (245, 245, 250))
        screen.blit(text, text.get_rect(center=rect.center))

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background, (0, 0))

        # Dim background for readability
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        screen.blit(overlay, (0, 0))

        # Title
        title = title_font.render("SUPERPOSITION", True, (245, 245, 250))
        screen.blit(title, title.get_rect(center=(screen_width // 2, 260)))

        # hint = hint_font.render("Mouse or ↑↓ + Enter | Esc exits", True, (190, 190, 205))
        # screen.blit(hint, hint.get_rect(center=(screen_width // 2, 305)))

        # draw buttons
        for i, (key, rect, label) in enumerate(buttons):
            hovered = rect.collidepoint(mouse_pos)
            selected = i == cursor or hovered
            if hovered:
                cursor = i
            draw_button(rect, label, hovered=hovered, selected=selected)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect, _label in buttons:
                    if rect.collidepoint(event.pos):
                        return key

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "exit"
                if event.key in (pygame.K_UP, pygame.K_w):
                    cursor = (cursor - 1) % len(buttons)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    cursor = (cursor + 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return buttons[cursor][0]

        pygame.display.flip()
        clock.tick(60)
