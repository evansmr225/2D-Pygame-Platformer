from settings import *
from player import *
from spider import *
from buzzsaw import *
from fish import *
from utils import *
from lavabubble import *
from fluid import *
import pygame
import sys
import random
import os

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x,y))

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
        #surface.blit(self.image, (self.rect.x, self.rect.y)) 

class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.blit(self.sprite_sheet,(0,0),(x,y,w,h))
        return sprite
    
    def get_sprite_from_id(self, id, image_width):
        y = (id // (image_width // TILESIZE)) * TILESIZE
        x = (id % (image_width // TILESIZE)) * TILESIZE
        return self.get_sprite(x, y, TILESIZE, TILESIZE)
    
class UI:
    def __init__(self, sprite_sheet, player_sprite_sheet, player_data):
        self.player_life_icon = player_sprite_sheet.get_sprite_from_id(13, 192)
        self.player_life_icon.set_colorkey(BLACK)
        original_width, original_height = self.player_life_icon.get_size()
        #self.player_life_icon = pygame.transform.scale(self.player_life_icon, (original_width * (3/4), original_height * (3/4)))

        self.font = pygame.font.SysFont("Verdana", 12)
        self.life_text = self.font.render(f": {player_data.lives}", True, WHITE)

    def draw(self, surface):
        surface.blit(self.player_life_icon, ((TILESIZE * 17), 0))
        surface.blit(self.life_text, ((TILESIZE * 18), 0))
    
class Camera:
    def __init__(self, player, left_border, right_border):
        self.player = player
        self.left_border = left_border
        self.right_border = right_border
        self.offset = pygame.math.Vector2(0, 0)
        self.offset_float = pygame.math.Vector2(0, 0)
        self.CONST = pygame.math.Vector2(-INTERNAL_DISPLAY_WIDTH // 2 + player.rect.w // 2, -INTERNAL_DISPLAY_HEIGHT // 4)

        self.offset_float.y = -self.CONST.y

    def scroll(self):
        self.offset_float.x += (self.player.rect.x - self.offset_float.x + self.CONST.x)
        #self.offset_float.y += (self.player.rect.y - self.offset_float.y + self.CONST.y)
        self.offset.x, self.offset.y = int(self.offset_float.x), int(self.offset_float.y)
        self.offset.x = max(self.left_border, self.offset.x)
        self.offset.x = min(self.offset.x, self.right_border - INTERNAL_DISPLAY_WIDTH)

class Level():
    def __init__(self, display, player_data):
        self.display = display
        self.map = read_csv('./test_3.csv')

        sprite_sheet = Spritesheet('./tile_map.png')
        player_sprite_sheet = Spritesheet('./player.png')
        
        self.empty_tiles = []
        self.layer_one_tiles = []

        self.collision_tiles = []
        self.one_way_collision_tiles = []
        self.damage_tiles = []

        self.spiders = []
        self.buzzsaws = []
        self.fish = []
        self.lava_bubbles = []

        self.bg = pygame.image.load("./Forest_Background_0.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (INTERNAL_DISPLAY_WIDTH, INTERNAL_DISPLAY_HEIGHT))
        self.fluid = Fluid(sprite_sheet, self.display)
        self.player = Player(player_sprite_sheet, self.display, (TILESIZE, TILESIZE * 19), self)

        self.ui = UI(sprite_sheet, player_sprite_sheet, player_data)
        
        self.completed = False
        self.reset = False
        self.exited = False

        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if col == SS_DIC.get("spider"):
                    spider = Spider((x * TILESIZE, y * TILESIZE), sprite_sheet, self.player)
                    self.damage_tiles.append(spider)
                    self.spiders.append(spider)
                elif col == SS_DIC.get("buzzsaw"):
                    path = [pygame.math.Vector2(10, 0), pygame.math.Vector2(0, -3)]
                    buzzsaw = Buzzsaw((x * TILESIZE, y * TILESIZE), sprite_sheet, path)
                    self.damage_tiles.append(buzzsaw)
                    self.buzzsaws.append(buzzsaw)
                elif col == SS_DIC.get("fish"):
                    path = [pygame.math.Vector2(0, -7)]
                    fish = Fish((x * TILESIZE, y * TILESIZE), sprite_sheet, path, 2)
                    self.damage_tiles.append(fish)
                    self.fish.append(fish)
                elif col == SS_DIC.get("lavabubble"):
                    path = [pygame.math.Vector2(0, -7)]
                    lava_bubble = LavaBubble((x * TILESIZE, y * TILESIZE), sprite_sheet, path, 2)
                    self.damage_tiles.append(lava_bubble)
                    self.lava_bubbles.append(lava_bubble)
                elif col == SS_DIC.get("empty"):
                    transparent_surface = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                    transparent_surface.fill((0, 0, 0, 0))
                    tile = Tile(transparent_surface, x * TILESIZE, y * TILESIZE)
                    self.empty_tiles.append(tile)
                else:
                    sprite = sprite_sheet.get_sprite_from_id(int(col), SPRITE_SHEET_WIDTH)
                    sprite.set_colorkey(BLACK)
                    tile = Tile(sprite, x * TILESIZE, y * TILESIZE)
                    
                    if col != SS_DIC.get("invisible_border"):
                        self.layer_one_tiles.append(tile)
                    
                    if col == SS_DIC.get("spikes"):
                        self.damage_tiles.append(tile)
                    elif col in SS_DIC.get("one_way"):
                        self.one_way_collision_tiles.append(tile)
                    elif col in SS_DIC.get("pass_through"):
                        pass
                    else:
                        self.collision_tiles.append(tile)
        self.camera = Camera(self.player, TILESIZE, TILESIZE * 80)

    def update_level(self, dt, player_data):
        self.camera.scroll()
        self.player.update(dt, self.collision_tiles, self.damage_tiles, self.one_way_collision_tiles, player_data)
        for spider in self.spiders: spider.update(self.collision_tiles, self.empty_tiles, self.one_way_collision_tiles, dt)
        for buzzsaw in self.buzzsaws: buzzsaw.update(dt)
        for lava_bubble in self.lava_bubbles: lava_bubble.update(dt)
        self.fluid.update()
        
        # draw everything
        self.display.fill((255, 255, 255))
        self.display.blit(self.bg, (0, 0))
        for tile in self.layer_one_tiles: tile.draw(self.display, self.camera)
        self.player.draw(self.camera)
        for spider in self.spiders: spider.draw(self.display, self.camera)
        for buzzsaw in self.buzzsaws: buzzsaw.draw(self.display, self.camera)
        for lava_bubble in self.lava_bubbles: lava_bubble.draw(self.display, self.camera)
        self.fluid.draw(self.display, self.camera)
        self.ui.draw(self.display)

    def pause_level(self, player_data, window):
        font = pygame.font.SysFont("Arial", 32)  # Font size for options
        menu_items = ["Restart Level", "Exit Level"]
        selected_item = 0  # Start by selecting the first option

         # Calculate the size and position of the textbox
        box_width = INTERNAL_DISPLAY_WIDTH // 2
        box_height = INTERNAL_DISPLAY_HEIGHT // 4
        box_x = (INTERNAL_DISPLAY_WIDTH - box_width) // 2
        box_y = (INTERNAL_DISPLAY_HEIGHT - box_height) // 2
        textbox_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Handle key presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_item = (selected_item + 1) % len(menu_items)
                    elif event.key == pygame.K_UP:
                        selected_item = (selected_item - 1) % len(menu_items)
                    elif event.key == pygame.K_RETURN:
                        # Perform action based on selected option
                        if selected_item == 0:
                            self.reset = True
                            running = False
                        elif selected_item == 1:
                            self.exited = True
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # continue to draw everything
            self.display.blit(self.bg, (0, 0))
            for tile in self.layer_one_tiles: tile.draw(self.display, self.camera)
            self.player.draw(self.camera)
            for spider in self.spiders: spider.draw(self.display, self.camera)
            for buzzsaw in self.buzzsaws: buzzsaw.draw(self.display, self.camera)
            for lava_bubble in self.lava_bubbles: lava_bubble.draw(self.display, self.camera)
            self.fluid.draw(self.display, self.camera)
            self.ui.draw(self.display, player_data)

            # Draw the textbox in the middle
            pygame.draw.rect(self.display, (200, 200, 200), textbox_rect)  # Light grey background
            pygame.draw.rect(self.display, BLACK, textbox_rect, 3)  # Black border

            # Render the options
            for i, item in enumerate(menu_items):
                if i == selected_item:
                    color = RED  # Highlight the selected item
                else:
                    color = BLACK
                text_surface = font.render(item, True, color)

                # Calculate the position to center the text in the textbox
                text_x = box_x + (box_width - text_surface.get_width()) // 2
                text_y = box_y + (box_height // 4) + i * (font.get_height() + 20)  # Space items vertically

                self.display.blit(text_surface, (text_x, text_y))
            
            # Scale and update display
            scaled_surface = pygame.transform.scale(self.display, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            window.blit(scaled_surface, (0, 0))
            pygame.display.flip()

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
        level = Level(internal_surface, player_data)
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