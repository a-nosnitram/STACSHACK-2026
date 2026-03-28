import pygame


# sprite attack animation
# frames 1.bmp and 2.bmp from assets/sprites/{character}/attack/
def draw_attack(character, x, y, screen, frame_idx=0, flipped=False):
    attack_frames = []
    for i in range(1, 3):
        frame = pygame.image.load(
            f"../assets/sprites/{character}/attack/{i}.bmp").convert_alpha()
        # scale sprite up
        frame = pygame.transform.scale(
            frame, (frame.get_width() * 8, frame.get_height() * 8))
        attack_frames.append(frame)

    # cycle through attack frames every 10 frames
    if len(attack_frames) % 10 == 0:
        frame_idx = (frame_idx) % len(attack_frames)
    else:
        frame_idx = (frame_idx // 10) % len(attack_frames)

    if flipped:
        attack_frames[frame_idx] = pygame.transform.flip(
            attack_frames[frame_idx], True, False)

    screen.blit(attack_frames[frame_idx], (x, y))
