import pygame
from sprites import draw_idle

# Initialize Pygame
pygame.init()

# screen settings
screen_width = 1400
screen_height = 700

# Set up the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("FireHUI")

background_image = pygame.image.load(
    "../assets/backgrounds/bg-stone.bmp").convert()
# set the background image to fill the entire window
background_image = pygame.transform.scale(
    background_image, (screen_width, screen_height))


# left player position
left_player_x = 50
left_player_y = screen_height - 350
left_player_name = "soph"

# right player position
right_player_x = screen_width - 350
right_player_y = screen_height - 350
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
