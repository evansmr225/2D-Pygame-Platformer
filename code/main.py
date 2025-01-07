from settings import *
from level import *

import pygame
import sys
import random
import os

# class made to easily pass player data like lives by reference
class PlayerData:
    def __init__(self):
        self.lives = 3

# Function to run an individual level of the game.
# The level class handles most of the game loop. View it for more information.
def run_level(level, internal_surface, window, player_data):
    clock = pygame.time.Clock()  # Create a clock to control the frame rate.
    
    # Main level loop.
    while not (level.completed or level.exited or level.reset):
        dt = clock.tick(60) * 0.001 * TARGET_FPS  # Calculate delta time for consistent movement.

        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle game window close.
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Handle key presses.
                if event.key == pygame.K_LEFT:  # Move player left.
                    level.player.left_key, level.player.facing_left = True, True
                if event.key == pygame.K_RIGHT:  # Move player right.
                    level.player.right_key, level.player.facing_left = True, False
                if event.key == pygame.K_SPACE:  # Jump action.
                    if level.player.state == PlayerState.NORMAL:
                        level.player.jump()
                if event.key == pygame.K_1:  # Pause the game.
                    level.pause_level(window)
                    clock.tick()  # Pause the clock.
                if event.key == pygame.K_f:
                    # Toggle between windowed and full screen
                    current_mode = pygame.display.get_surface().get_flags()
                    if current_mode & pygame.FULLSCREEN:
                        # Switch to windowed mode
                        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                    else:
                        # Switch to full screen
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            if event.type == pygame.KEYUP:  # Handle key releases.
                if event.key == pygame.K_LEFT:
                    level.player.left_key = False
                elif event.key == pygame.K_RIGHT:
                    level.player.right_key = False
                elif event.key == pygame.K_SPACE:
                    if level.player.is_jumping:  # Shorten jump when releasing space.
                        level.player.velocity.y *= 0.25
                        level.player.is_jumping = False
            if event.type == pygame.VIDEOEXPOSE:  # Handle screen exposure event.
                clock.tick()

        # Update the internal display.
        internal_surface.fill(LIGHT_BLUE)  # Fill display with background color.
        level.update_level(dt, player_data)  # Update level logic and draw level.

        # Scale the internal surface to fit the game window.
        scaled_surface = pygame.transform.scale(internal_surface, window.get_size())
        window.blit(scaled_surface, (0, 0))  # Draw the scaled surface onto the window.
        pygame.display.flip()  # Update the display.

    # Handle level exit conditions and return appropriate values.
    if level.exited:
        clock.tick()
        pygame.mixer.music.stop()  # Stop any playing music.
        return 0
    elif level.reset:
        clock.tick()
        pygame.mixer.music.stop()
        return 1
    elif level.completed:
        clock.tick()
        pygame.mixer.music.stop()
        return 2
    else:
        clock.tick()
        pygame.mixer.music.stop()
        return -1
    
# Function to display a transition screen between levels.
def run_transition_screen(internal_surface, window, duration=1):
    start_time = pygame.time.get_ticks()  # Record the start time.

    while True:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Calculate elapsed time.
        if elapsed_time >= duration:  # Break loop after the duration.
            break

        # Handle events during the transition.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Toggle between windowed and full screen
                    current_mode = pygame.display.get_surface().get_flags()
                    if current_mode & pygame.FULLSCREEN:
                        # Switch to windowed mode
                        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                    else:
                        # Switch to full screen
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Fill the screen with black during the transition.
        internal_surface.fill(BLACK)
        scaled_surface = pygame.transform.scale(internal_surface, window.get_size())
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Function to display a "Game Over" screen.
def run_game_over_screen(internal_surface, window, duration=1):
    start_time = pygame.time.get_ticks()  # Record the start time.
    font = pygame.font.SysFont("Verdana", 24)  # Font for the "Game Over" message.
    game_over_text = font.render('Game Over', True, WHITE)  # Render the text.
    text_rect = game_over_text.get_rect()
    text_rect.center = (INTERNAL_DISPLAY_WIDTH // 2, INTERNAL_DISPLAY_HEIGHT // 2)  # Center the text.

    while True:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        if elapsed_time >= duration:  # Break loop after the duration.
            break

        # Handle events during the screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    # Toggle between windowed and full screen
                    current_mode = pygame.display.get_surface().get_flags()
                    if current_mode & pygame.FULLSCREEN:
                        # Switch to windowed mode
                        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                    else:
                        # Switch to full screen
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Display the "Game Over" message.
        internal_surface.fill(BLACK)
        internal_surface.blit(game_over_text, text_rect)
        scaled_surface = pygame.transform.scale(internal_surface, window.get_size())
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# Function to start and manage the entire game flow.
def run_game(internal_surface, window):
    player_data = PlayerData() # Initialize player data.
    level_return_value = 1 # Track the current level state.
    # Run each level and manage transitions.
    while level_return_value == 1 and player_data.lives > 0:
        run_transition_screen(internal_surface, window, 1)
        bg_image = pygame.image.load(resource_path(os.path.join("assets", "images", "Forest_Background_0.png"))).convert_alpha()
        level = Level(internal_surface, player_data, "water", resource_path(os.path.join("assets", "sounds", "level_1_music.wav")), bg_image, resource_path(os.path.join("assets", "levels", "level_1.csv")), 1360)
        level_return_value = run_level(level, internal_surface, window, player_data)
    if level_return_value == 0:
        return
    level_return_value = 1
    while level_return_value == 1 and player_data.lives > 0:
        run_transition_screen(internal_surface, window, 1)
        bg_image = pygame.image.load(resource_path(os.path.join("assets", "images", "Sky_Background_0.png"))).convert_alpha()
        level = Level(internal_surface, player_data, "air", resource_path(os.path.join("assets", "sounds", "level_2_music.wav")), bg_image, resource_path(os.path.join("assets", "levels", "level_2.csv")), 880)
        level_return_value = run_level(level, internal_surface, window, player_data)
    level_return_value = 1
    while level_return_value == 1 and player_data.lives > 0:
        run_transition_screen(internal_surface, window, 1)
        bg_image = pygame.image.load(resource_path(os.path.join(".", "Castle_Background_0.png"))).convert_alpha()
        level = Level(internal_surface, player_data, "lava", resource_path(os.path.join("assets", "sounds", "level_3_music.wav")), bg_image, resource_path(os.path.join("assets", "level_3.csv")), 880)
        level_return_value = run_level(level, internal_surface, window, player_data)
    
    if player_data.lives <= 0:
        run_game_over_screen(internal_surface, window) # Display "Game Over."
    else:
        run_finish_screen(internal_surface, window) # Display victory screen.

# Function to display the victory screen after completing the game.
def run_finish_screen(internal_surface, window):
    font = pygame.font.SysFont("Arial", 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_f:
                    # Toggle between windowed and full screen
                    current_mode = pygame.display.get_surface().get_flags()
                    if current_mode & pygame.FULLSCREEN:
                        # Switch to windowed mode
                        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                    else:
                        # Switch to full screen
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
        # Fill the background with black
        internal_surface.fill(BLACK)

        # Render the Finish Text
        render_multiline_text("Congragulations!\nYou beat the game.", font, WHITE, internal_surface, 
                              INTERNAL_DISPLAY_WIDTH // 7, INTERNAL_DISPLAY_HEIGHT // 3)

        scaled_surface = pygame.transform.scale(internal_surface, window.get_size())
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

def run_menu(internal_surface, window):
    font = pygame.font.SysFont("Arial", 24)
    menu_items = ["Start Game", "Quit"]
    selected_item = 0

    # Calculate the total height of the menu (sum of item heights + spacing)
    total_menu_height = len(menu_items) * font.get_height() + (len(menu_items) - 1) * 20  # 20 pixels of vertical spacing

    # Calculate the starting y position to vertically center the menu
    start_y = (INTERNAL_DISPLAY_HEIGHT - total_menu_height) // 2

    # Set a fixed x position to align the left sides of menu items
    x_pos = INTERNAL_DISPLAY_WIDTH // 4  

    # Prepare rectangles for menu items
    menu_rects = []
    for i, item in enumerate(menu_items):
        # Calculate y position for each menu item, evenly spaced
        y_pos = start_y + i * (font.get_height() + 20)  
        
        # Render text (no need to calculate text width now)
        text_surface = font.render(item, True, BLACK)
        
        # Create a rectangle for each item with the fixed x and calculated y position
        menu_rect = pygame.Rect(x_pos, y_pos, text_surface.get_width(), text_surface.get_height())
        menu_rects.append(menu_rect)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    # Move down in the menu
                    selected_item = (selected_item + 1) % len(menu_items)
                elif event.key == pygame.K_UP:
                    # Move up in the menu
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    # If Enter is pressed, perform the action for the selected item
                    if selected_item == 0:
                        run_game(internal_surface, window)
                    elif selected_item == 1:
                        running = False  # Quit the game
                elif event.key == pygame.K_f:
                    # Toggle between windowed and full screen
                    current_mode = pygame.display.get_surface().get_flags()
                    if current_mode & pygame.FULLSCREEN:
                        # Switch to windowed mode
                        window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                    else:
                        # Switch to full screen
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Fill the background with white
        internal_surface.fill(WHITE)

        # Render the "Pygame Platformer" text
        text = font.render("Pygame Platformer", True, BLACK)

        # Position the text at the top center
        text_rect = text.get_rect(center=(INTERNAL_DISPLAY_WIDTH // 2, 20))  # Y-offset of 20 for top placement

        # Blit the text onto the screen
        internal_surface.blit(text, text_rect)

        # Render each menu item
        for i, item in enumerate(menu_items):
            if i == selected_item:
                color = RED  # Highlight the selected item
            else:
                color = BLACK
            
            # Render text
            text_surface = font.render(item, True, color)
            internal_surface.blit(text_surface, menu_rects[i].topleft)

        scaled_surface = pygame.transform.scale(internal_surface, window.get_size())
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()


# Main function to start the game.
def main():
    pygame.init()  # Initialize Pygame.

    # Create internal surface and window.
    internal_surface = pygame.Surface((INTERNAL_DISPLAY_WIDTH, INTERNAL_DISPLAY_HEIGHT))
    window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
    pygame.display.set_caption("Platformer Game")  # Set window title.

    run_menu(internal_surface, window)  # Start with the main menu.
    
# Run the main function.
main()