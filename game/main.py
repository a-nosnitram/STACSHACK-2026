import pygame

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((1400, 700))
pygame.display.set_caption("FireHUI")

background_image = pygame.image.load(
    "../assets/backgrounds/bg-stone.bmp").convert()
# set the background image to fill the entire window
background_image = pygame.transform.scale(background_image, (1400, 700))

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    # Fill the screen with the background image
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()

    clock.tick(60)

# Quit Pygame
pygame.quit()
