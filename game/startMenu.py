import pygame


def run_start_menu(screen: pygame.Surface, background):
    if not pygame.get_init():
        pygame.init()

    clock = pygame.time.Clock()

    button_font = pygame.font.Font("assets/fonts/Silkscreen-Regular.ttf", 22)

    screen_width, screen_height = screen.get_size()

    button_width = 240
    button_height = 50
    button_gap = 18

    start_y = 420  # ниже, чтобы сверху осталось место под логотип

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

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background, (0, 0))

        normal_color = (40, 40, 40)
        hover_color = (90, 90, 90)
        border_color = (255, 255, 255)

        def draw_button(rect, text):
            color = hover_color if rect.collidepoint(mouse_pos) else normal_color
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=6)

            text_surface = button_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        draw_button(start_button, "START")
        draw_button(character_button, "CHOOSE CHARACTERS")
        draw_button(exit_button, "EXIT")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    return "start"
                if character_button.collidepoint(event.pos):
                    return "character"
                if exit_button.collidepoint(event.pos):
                    return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "exit"

        pygame.display.flip()
        clock.tick(60)