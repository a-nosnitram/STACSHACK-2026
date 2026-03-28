import pygame
import json
import os


def load_stages():
    with open("game/stages.json", "r") as f:
        return json.load(f)["stages"]


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


def _lerp(a: float, b: float, t: float) -> float:
    return float(a + (b - a) * t)


def _lerp_color(c1, c2, t: float):
    t = _clamp01(t)
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


def _draw_panel(
    screen,
    rect: pygame.Rect,
    *,
    fill=(24, 24, 30),
    outline=(85, 85, 98),
    radius=14,
    shadow=True,
):
    """Rounded panel with subtle shadow + outline."""
    if shadow:
        shadow_surf = pygame.Surface((rect.w + 10, rect.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, 90),
            pygame.Rect(5, 5, rect.w, rect.h),
            border_radius=radius,
        )
        screen.blit(shadow_surf, (rect.x - 5, rect.y - 5))

    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, outline, rect, width=2, border_radius=radius)


def _draw_smooth_bar(
    screen,
    rect: pygame.Rect,
    *,
    ratio: float,
    fill_color=(70, 235, 120),
    track_color=(34, 34, 42),
    radius=14,
    flipped=False,
):
    """Rounded bar with padding + gloss highlight."""
    ratio = _clamp01(ratio)
    _draw_panel(screen, rect, fill=track_color, outline=(85, 85, 98), radius=radius, shadow=True)

    pad = 4
    inner = pygame.Rect(rect.x + pad, rect.y + pad, rect.w - 2 * pad, rect.h - 2 * pad)
    inner_radius = max(0, radius - pad)

    fill_w = int(inner.w * ratio)
    if fill_w <= 0:
        return

    fill_rect = pygame.Rect(inner.x, inner.y, fill_w, inner.h)
    if flipped:
        fill_rect.x = inner.right - fill_w

    pygame.draw.rect(screen, fill_color, fill_rect, border_radius=inner_radius)

    # Subtle gloss on top half
    gloss_h = max(1, fill_rect.h // 2)
    gloss = pygame.Surface((fill_rect.w, gloss_h), pygame.SRCALPHA)
    pygame.draw.rect(
        gloss,
        (255, 255, 255, 35),
        pygame.Rect(0, 0, gloss.get_width(), gloss.get_height()),
        border_radius=max(0, inner_radius - 2),
    )
    screen.blit(gloss, (fill_rect.x, fill_rect.y))


def draw_hp_bar(screen, hp, x, y, name, flipped=False, max_hp=100.0):
    pygame.font.init()

    max_hp = float(max_hp) if max_hp else 1.0
    hp = max(0.0, float(hp))
    ratio = hp / max_hp

    rect = pygame.Rect(int(x), int(y), 320, 34)
    fill = _lerp_color((240, 70, 70), (70, 235, 120), ratio)  # red -> green
    _draw_smooth_bar(screen, rect, ratio=ratio, fill_color=fill, radius=14, flipped=flipped)

    # Label inside the bar (avoids overlapping the progress bar at the top).
    font = pygame.font.Font(None, 22)
    label = font.render(f"{name}  {int(hp)}/{int(max_hp)}", True, (245, 245, 250))
    label_y = rect.y + (rect.h - label.get_height()) // 2
    if flipped:
        label_x = rect.right - label.get_width() - 10
    else:
        label_x = rect.x + 10
    screen.blit(label, (label_x, label_y))


def draw_progress_bar(screen, current_stage, stages, frame):
    pygame.font.init()

    total_stages = len(stages)
    screen_width, _ = screen.get_size()

    # Progress bar dimensions and position
    bar_width = 460
    # Slightly thinner track so the stage circles can "sit" over it.
    bar_height = 34
    bar_x = (screen_width - bar_width) // 2
    bar_y = 50

    rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    completed = max(0, int(current_stage) - 1)
    fill_ratio = 0.0 if total_stages <= 0 else completed / float(total_stages)

    # Single smooth bar looks cleaner than filling each stage segment.
    _draw_smooth_bar(
        screen,
        rect,
        ratio=fill_ratio,
        fill_color=(70, 235, 120),
        track_color=(30, 30, 38),
        radius=16,
        flipped=False,
    )

    # Stage markers (circles) + numbers
    font = pygame.font.Font(None, 32)
    for i in range(total_stages):
        t = 0.5 if total_stages == 1 else i / float(total_stages - 1)
        cx = int(rect.x + 18 + t * (rect.w - 36))
        cy = int(rect.y + rect.h // 2)

        if i < completed:
            dot = (70, 235, 120)
        elif i == completed:
            dot = (250, 210, 80)  # current stage
        else:
            dot = (95, 95, 110)

        # Bigger circles than the track height so they overlap ("float over") the bar.
        outer_r = 17
        inner_r = 14
        pygame.draw.circle(screen, (20, 20, 24), (cx, cy), outer_r)
        pygame.draw.circle(screen, dot, (cx, cy), inner_r)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), inner_r, width=2)

        text = font.render(str(i + 1), True, (10, 10, 14))
        screen.blit(text, text.get_rect(center=(cx, cy + 1)))

    # Draw "position picture" for the current stage
    if current_stage <= total_stages:
        stage_info = stages[min(current_stage - 1, total_stages - 1)]
        img_path = stage_info.get("image")
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            
            # Scale image proportionally to fit within a reasonable size (e.g., 200x200)
            max_size = 200
            w, h = img.get_size()
            scale = min(max_size / w, max_size / h)
            new_size = (int(w * scale), int(h * scale))
            img = pygame.transform.scale(img, new_size)

            img_x = (screen_width - img.get_width()) // 2
            img_y = bar_y + bar_height + 20

            # Draw a nicer frame for the image
            frame_rect = pygame.Rect(img_x - 8, img_y - 8, img.get_width() + 16, img.get_height() + 16)
            _draw_panel(screen, frame_rect, fill=(18, 18, 22), outline=(120, 120, 135), radius=14, shadow=True)
            screen.blit(img, (img_x, img_y))

            # Draw pose name
            pose_text = font.render(f"Pose: {stage_info['pose']}", True, (245, 245, 250))
            screen.blit(pose_text, (img_x, img_y + img.get_height() + 12))


def draw_win_screen(screen, winner):
    pygame.font.init()
    screen_width, screen_height = screen.get_size()

    # Dim the background
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    # Center card
    card_w, card_h = 760, 260
    card_rect = pygame.Rect(
        (screen_width - card_w) // 2,
        (screen_height - card_h) // 2,
        card_w,
        card_h,
    )
    _draw_panel(screen, card_rect, fill=(20, 20, 26), outline=(120, 120, 140), radius=22, shadow=True)

    # Title
    title_font = pygame.font.Font(None, 110)
    if str(winner).upper() == "TIE":
        title = "DRAW"
        title_color = (250, 210, 80)
    else:
        title = f"{str(winner).upper()} WINS"
        title_color = (70, 235, 120)

    title_surf = title_font.render(title, True, title_color)
    title_rect = title_surf.get_rect(center=(card_rect.centerx, card_rect.y + 95))
    screen.blit(title_surf, title_rect)

    # Subtitle / hint
    hint_font = pygame.font.Font(None, 36)
    hint = "Press ESC / ENTER / SPACE to exit"
    hint_surf = hint_font.render(hint, True, (230, 230, 240))
    hint_rect = hint_surf.get_rect(center=(card_rect.centerx, card_rect.y + 175))
    screen.blit(hint_surf, hint_rect)

    # Small accent line
    pygame.draw.line(
        screen,
        (90, 90, 105),
        (card_rect.x + 60, card_rect.y + 135),
        (card_rect.right - 60, card_rect.y + 135),
        2,
    )