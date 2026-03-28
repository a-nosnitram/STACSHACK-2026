import asyncio
import pygame
from game.attack import Attack
from game.sprites import draw_idle
from game.ui import draw_progress_bar, load_stages

async def run_game():
    # Initialize Pygame
    pygame.init()

    # screen settings
    screen_width = 1400
    screen_height = 700

    # Set up the game window
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("FireHUI")

    background_image = pygame.image.load(
        "assets/backgrounds/bg-forest.bmp").convert()
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
    fireballs = []
    
    # Initialize stages
    stages = load_stages()
    current_stage = 1
    
    while running:
        # Fill the screen with the background image
        screen.blit(background_image, (0, 0))

        # draw idle sprites
        draw_idle(left_player_name, left_player_x,
                  left_player_y, screen, frame)
        draw_idle(right_player_name, right_player_x,
                  right_player_y, screen, frame, flipped=True)

        # Draw progress bar
        draw_progress_bar(screen, current_stage, stages, frame)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # fiereballs on keypress for now
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fireballs.append(
                        Attack(
                            "fireball",
                            x=left_player_x + 220,
                            y=left_player_y + 40,
                            target_x=right_player_x - 40,
                            direction=1,
                        )
                    )
                if event.key == pygame.K_RETURN:
                    fireballs.append(
                        Attack(
                            "fireball",
                            x=right_player_x - 40,
                            y=right_player_y + 40,
                            target_x=left_player_x + 40,
                            direction=-1,
                        )
                    )
                # simulate progression with 'p'
                if event.key == pygame.K_p:
                    current_stage += 1
                    if current_stage > len(stages):
                        current_stage = 1 # reset for now

        # update and draw fireballs
        for fireball in fireballs:
            fireball.update()
            fireball.draw(screen)
        fireballs = [fireball for fireball in fireballs if fireball.active]
        pygame.display.flip()

        frame += 1
        clock.tick(60)
        await asyncio.sleep(0)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(run_game())
