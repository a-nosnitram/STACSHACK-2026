import pygame
from sprites import draw_idle

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((1400, 700))
pygame.display.set_caption("FireHUI")

background_image = pygame.image.load(
    "../assets/backgrounds/bg-stone.bmp").convert()
# set the background image to fill the entire window
background_image = pygame.transform.scale(background_image, (1400, 700))


# left player position
left_player_x = 50
left_player_y = 300
left_player_name = "soph"

# right player position
right_player_x = 1000
right_player_y = 300
right_player_name = "yehor"

# Game loop
clock = pygame.time.Clock()
running = True
frame = 0

while running:
    # Fill the screen with the background image
    screen.blit(background_image, (0, 0))

    # draw idle sprites
    draw_idle(left_player_name, left_player_x, left_player_y, screen, frame)
    draw_idle(right_player_name, right_player_x,
              right_player_y, screen, frame, flipped=True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()

    frame += 1
    clock.tick(60)

# Quit Pygame
pygame.quit()
