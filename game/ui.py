import pygame
import json
import os


def load_stages():
    with open("game/stages.json", "r") as f:
        return json.load(f)["stages"]


def draw_progress_bar(screen, current_stage, stages):
    total_stages = len(stages)
    screen_width = screen.get_size()

    # Progress bar dimensions and position
    bar_width = 400
    bar_height = 40
    bar_x = (screen_width - bar_width) // 2
    bar_y = 50

    # Draw background bar
    pygame.draw.rect(
        screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=10
    )

    # Draw stages
    stage_width = bar_width // total_stages
    for i in range(total_stages):
        stage_rect = pygame.Rect(
            bar_x + i * stage_width, bar_y, stage_width, bar_height
        )

        # Draw stage divider
        if i > 0:
            pygame.draw.line(
                screen,
                (100, 100, 100),
                (bar_x + i * stage_width, bar_y),
                (bar_x + i * stage_width, bar_y + bar_height),
                2,
            )

        # Highlight completed/current stages
        if i < current_stage:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                stage_rect,
                border_radius=10 if (i == 0 and total_stages == 1) else 0,
            )

        # Draw stage number
        font = pygame.font.SysFont(None, 36)
        text = font.render(str(i + 1), True, (255, 255, 255))
        text_rect = text.get_rect(center=stage_rect.center)
        screen.blit(text, text_rect)

    # Draw "position picture" for the current stage
    if current_stage <= total_stages:
        stage_info = stages[min(current_stage - 1, total_stages - 1)]
        img_path = stage_info.get("image")
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            # Scale it a bit
            img = pygame.transform.scale(
                img, (img.get_width() * 4, img.get_height() * 4)
            )
            img_x = (screen_width - img.get_width()) // 2
            img_y = bar_y + bar_height + 20

            # Draw a frame for the image
            pygame.draw.rect(
                screen,
                (200, 200, 200),
                (img_x - 5, img_y - 5, img.get_width() + 10, img.get_height() + 10),
                2,
            )
            screen.blit(img, (img_x, img_y))

            # Draw pose name
            pose_text = font.render(
                f"Pose: {stage_info['pose']}", True, (255, 255, 255)
            )
            screen.blit(pose_text, (img_x, img_y + img.get_height() + 10))
