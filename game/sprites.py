import pygame

# sprite idle animation
# frames 1.bmp and 2.bmp from assets/sprites/{character}/idle/


def draw_idle(character, x, y, screen, frame_idx=0, flipped=False):
    idle_frames = []
    for i in range(1, 3):
        frame = pygame.image.load(
            f"assets/sprites/{character}/idle/{i}.bmp").convert_alpha()
        # scale sprite up
        frame = pygame.transform.scale(
            frame, (frame.get_width() * 8, frame.get_height() * 8))
        idle_frames.append(frame)

    # cycle through idle frames every 10 frames
    if len(idle_frames) % 10 == 0:
        frame_idx = (frame_idx) % len(idle_frames)
    else:
        frame_idx = (frame_idx // 10) % len(idle_frames)

    if flipped:
        idle_frames[frame_idx] = pygame.transform.flip(
            idle_frames[frame_idx], True, False)

    screen.blit(idle_frames[frame_idx], (x, y))
