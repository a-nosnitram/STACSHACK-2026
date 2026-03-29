import asyncio
import pygame
from game.attack import Attack
from game.sprites import draw_idle
from game.ui import draw_progress_bar, load_stages, draw_win_screen, draw_hp_bar
from shared.bus import game_to_vision, vision_to_game
from game.menu import run_pose_menu
from game.startScreen import run_start_screen
from game.startMenu import run_start_menu
from game.character_select import run_character_select


def handle_win_condition(screen, left_hp, right_hp, left_name, right_name, game_over, winner):
    if not game_over:
        if left_hp <= 0:
            game_over = True
            winner = right_name
            left_hp = 0
            print(f"THE USER {winner.upper()} WON!!!!")
        elif right_hp <= 0:
            game_over = True
            winner = left_name
            right_hp = 0
            print(f"THE USER {winner.upper()} WON!!!!")

    if game_over:
        draw_win_screen(screen, winner)

    return left_hp, right_hp, game_over, winner


def handle_win_condition(screen, left_hp, right_hp, left_name, right_name, game_over, winner):
    if not game_over:
        if left_hp <= 0:
            game_over = True
            winner = right_name
            left_hp = 0
            print(f"THE USER {winner.upper()} WON!!!!")
        elif right_hp <= 0:
            game_over = True
            winner = left_name
            right_hp = 0
            print(f"THE USER {winner.upper()} WON!!!!")

    if game_over:
        draw_win_screen(screen, winner)

    return left_hp, right_hp, game_over, winner


async def run_game():
    # Initialize Pygame
    pygame.init()

    # screen settings
    screen_width = 1400
    screen_height = 700

    # call settings
    surface = pygame.display.set_mode((screen_width, screen_height))

    startscreen_background_image = pygame.image.load(
        "assets/backgrounds/bg-forest.bmp"
    ).convert()
    startscreen_background_image = pygame.transform.scale(
        startscreen_background_image, (screen_width, screen_height))

    # Start screen view
    run_start_screen(surface, startscreen_background_image)

    # all the poses that we obviously have implemented so far
    poses = ["squat", "bear", "plank", "bug", "lunge"]

    # дефолтные персонажи
    selected_characters = {
        "left": "soph",
        "right": "yehor",
    }

    # Главное меню
    while True:
        menu_result = run_start_menu(surface, startscreen_background_image)

        if menu_result == "exit":
            pygame.quit()
            return

        elif menu_result == "character":
            result = run_character_select(surface, startscreen_background_image)
            if result is not None:
                selected_characters = result
            # после выбора персонажей просто возвращаемся в главное меню
            continue

        elif menu_result == "start":
            selected_poses = run_pose_menu(surface, poses, startscreen_background_image)
            if selected_poses == []:
                continue

            break

    # send user-selected settings to vision
    await game_to_vision.put(
        {"type": "start_match", "poses": selected_poses, "rounds_ms": 5000}
    )

    # Set up the game window
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("SUPERPOSITION")

    background_image = pygame.image.load(
        "assets/backgrounds/bg-forest.bmp").convert()
    # set the background image to fill the entire window
    background_image = pygame.transform.scale(
        background_image, (screen_width, screen_height)
    )

    # left player position
    left_player_x = 50
    left_player_y = screen_height - 350
    left_player_hp = 100
    left_player_name = selected_characters["left"]

    # right player position
    right_player_x = screen_width - 350
    right_player_y = screen_height - (350 + 32 * 8)
    right_player_hp = 100
    right_player_name = selected_characters["right"]

    # Game loop
    clock = pygame.time.Clock()
    running = True
    frame = 0
    fireballs = []

    # Initialize stages
    stages = load_stages()
    current_stage = 1

    rounds_total = len(stages)
    rounds_played = 0
    end_after_fireballs = False

    last_player = None
    game_over = False
    winner = None

    while running:
        # Fill the screen with the background image
        screen.blit(background_image, (0, 0))

        while not vision_to_game.empty():
            msg = await vision_to_game.get()
            if msg["type"] == "round_result" and not game_over:
                last_player = msg["winner"]

        # draw idle sprites
        draw_idle(left_player_name, left_player_x,
                  left_player_y, screen, frame)
        draw_idle(
            right_player_name,
            right_player_x,
            right_player_y,
            screen,
            frame,
            flipped=True,
        )

        draw_idle(
            "anastasia",
            left_player_x + 220,
            left_player_y,
            screen, frame
        )

        draw_idle(
            "fedor",
            right_player_x - 220,
            left_player_y,
            screen, frame, flipped=True
        )

        # Draw progress bar
        draw_progress_bar(screen, current_stage, stages, frame)

        # Draw HP bars
        draw_hp_bar(screen, left_player_hp, 40, 25,
                    left_player_name, max_hp=100.0)
        draw_hp_bar(
            screen,
            right_player_hp,
            screen_width - 40 - 320,
            25,
            right_player_name,
            flipped=True,
            max_hp=100.0,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # If game is over, any of these keys will exit
                if game_over and event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    running = False

                if not game_over:
                    # Trigger fireballs manually
                    if event.key == pygame.K_SPACE:
                        last_player = "1"  # Left player attacks
                    elif event.key == pygame.K_RETURN:
                        last_player = "2"  # Right player attacks

        if last_player is not None and not game_over:
            if last_player == "1":
                fireballs.append(
                    Attack(
                        "fireball",
                        x=left_player_x + 220,
                        y=left_player_y + 40,
                        target_x=right_player_x - 40,
                        direction=1,
                        sender="1",
                    )
                )
            else:
                fireballs.append(
                    Attack(
                        "fireball",
                        x=right_player_x - 40,
                        y=right_player_y + 40,
                        target_x=left_player_x + 40,
                        direction=-1,
                        sender="2",
                    )
                )

            # A "round" ends when a winner is decided and an attack is launched.
            rounds_played += 1
            if current_stage < rounds_total:
                current_stage += 1

            if rounds_total > 0 and rounds_played >= rounds_total:
                # Let the final projectile land, then end the game.
                end_after_fireballs = True

            last_player = None

        # update and draw fireballs
        for fireball in fireballs:
            old_active = fireball.active
            fireball.update()
            fireball.draw(screen)

            # Check for hit (when it becomes inactive)
            if old_active and not fireball.active:
                if fireball.sender == "1":
                    right_player_hp -= 20
                else:
                    left_player_hp -= 20

        fireballs = [fireball for fireball in fireballs if fireball.active]

        # Check for win condition
        left_player_hp, right_player_hp, game_over, winner = handle_win_condition(
            screen,
            left_player_hp,
            right_player_hp,
            left_player_name,
            right_player_name,
            game_over,
            winner,
        )

        # End the game once all rounds are done and the last projectile has landed.
        if end_after_fireballs and not game_over and not fireballs:
            game_over = True
            if left_player_hp > right_player_hp:
                winner = left_player_name
            elif right_player_hp > left_player_hp:
                winner = right_player_name
            else:
                winner = "TIE"
            draw_win_screen(screen, winner)

        pygame.display.flip()

        frame += 1
        clock.tick(60)
        await asyncio.sleep(0)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(run_game())