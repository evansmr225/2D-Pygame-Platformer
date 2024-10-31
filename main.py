from settings import *
from level import *

import pygame
import sys
import random
import os


class PlayerData:
    def __init__(self):
        self.lives = 3

def run_level(level, internal_surface, window, player_data):
    clock = pygame.time.Clock()
    while level.completed == False and level.exited == False and level.reset == False:
        dt = clock.tick(60) *.001 * TARGET_FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    level.player.left_key, level.player.facing_left = True, True
                if event.key == pygame.K_RIGHT:
                    level.player.right_key, level.player.facing_left = True, False
                if event.key == pygame.K_SPACE:
                    if level.player.state == PlayerState.NORMAL:
                        level.player.jump()
                if event.key == pygame.K_ESCAPE:
                    level.pause_level(player_data, window)
                    clock.tick()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    level.player.left_key = False
                elif event.key == pygame.K_RIGHT:
                    level.player.right_key = False
                elif event.key == pygame.K_SPACE:
                    if level.player.is_jumping:
                        level.player.velocity.y *= 0.25
                        level.player.is_jumping = False
            if event.type == pygame.VIDEOEXPOSE:
                clock.tick()

        internal_surface.fill(LIGHT_BLUE)
        level.update_level(dt, player_data)
        
        scaled_surface = pygame.transform.scale(internal_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()
    
    if level.exited:
        return 0
    elif level.reset:
        return 1
    elif level.completed:
        return 2
    else:
        return -1
    
def run_transition_screen(internal_surface, window, duration=1):
    start_time = pygame.time.get_ticks()  

    while True:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  
        if elapsed_time >= duration:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        internal_surface.fill(BLACK)
        scaled_surface = pygame.transform.scale(internal_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

def run_game_over_screen(internal_surface, window, duration=1):
    start_time = pygame.time.get_ticks()  
    font = pygame.font.SysFont("Verdana", 24)
    game_over_text = font.render('Game Over', True, WHITE)
    text_rect = game_over_text.get_rect()
    text_rect.center = (INTERNAL_DISPLAY_WIDTH // 2, INTERNAL_DISPLAY_HEIGHT // 2)

    while True:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  
        if elapsed_time >= duration:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        internal_surface.fill(BLACK)
        internal_surface.blit(game_over_text, text_rect)
        scaled_surface = pygame.transform.scale(internal_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

def run_game(internal_surface, window):
    player_data = PlayerData()
    level_return_value = 1
    while level_return_value == 1 and player_data.lives > 0:
        run_transition_screen(internal_surface, window, 1)
        bg_image = pygame.image.load("./Forest_Background_0.png").convert_alpha()
        level = Level(internal_surface, player_data, "water", bg_image, './level_1.csv')
        level_return_value = run_level(level, internal_surface, window, player_data)
    if player_data.lives <= 0:
        run_game_over_screen(internal_surface, window)

def run_menu(internal_surface, window):
    font = pygame.font.SysFont("Arial", 24)
    menu_items = ["Start Game", "Options", "Quit"]
    selected_item = 0

    # Calculate the total height of the menu (sum of item heights + spacing)
    total_menu_height = len(menu_items) * font.get_height() + (len(menu_items) - 1) * 20  # 20 pixels of vertical spacing

    # Calculate the starting y position to vertically center the menu
    start_y = (INTERNAL_DISPLAY_HEIGHT - total_menu_height) // 2

    # Set a fixed x position to align the left sides of menu items
    x_pos = INTERNAL_DISPLAY_WIDTH // 4  # Adjust this for desired horizontal alignment (e.g. left 25% of the screen)

    # Prepare rectangles for menu items
    menu_rects = []
    for i, item in enumerate(menu_items):
        # Calculate y position for each menu item, evenly spaced
        y_pos = start_y + i * (font.get_height() + 20)  # 20 pixels of vertical space between items
        
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
                        print("Options selected")
                    elif selected_item == 2:
                        running = False  # Quit the game

        # Fill the background with white
        internal_surface.fill(WHITE)

        # Render each menu item
        for i, item in enumerate(menu_items):
            if i == selected_item:
                color = RED  # Highlight the selected item
            else:
                color = BLACK
            
            # Render text
            text_surface = font.render(item, True, color)
            internal_surface.blit(text_surface, menu_rects[i].topleft)

        scaled_surface = pygame.transform.scale(internal_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()


def main():
    pygame.init()

    internal_surface = pygame.Surface((INTERNAL_DISPLAY_WIDTH, INTERNAL_DISPLAY_HEIGHT))

    window_size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    window = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
    pygame.display.set_caption("Platformer Game")

    run_menu(internal_surface, window)
    

main()