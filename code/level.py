from settings import *
from spritesheet import *
from player import *
from spider import *
from buzzsaw import *
from fish import *
from utils import *
from lavabubble import *
from fluid import *
from bird import *
from background import *
from falling_platform import *
from endgoal import *
from UI import *
from camera import *
from firebar import *
from tile import *

import sys
import pygame

class Level():
    def __init__(self, display, player_data, fluid_type, level_music, background_image, csv_file, right_border):
        # Initialize the level, loading assets and setting up initial game objects
        self.display = display  # The main display surface to render the level
        self.map = read_csv(csv_file)  # Load the map from a CSV file that defines the level layout
        pygame.mixer.music.load(level_music)  # Load background music
        pygame.mixer.music.play(-1)  # Play the music on loop

        # Initialize sprite sheets for tiles and the player
        sprite_sheet = Spritesheet('tile_map.png')
        player_sprite_sheet = Spritesheet('player.png')
        
        # Lists which hold data of tiles and entities so they can be updated and drawn
        self.empty_tiles = []
        self.layer_one_tiles = []

        self.collision_tiles = []
        self.one_way_collision_tiles = []
        self.damage_tiles = []

        self.spiders = []
        self.buzzsaws = []
        self.fish = []
        self.lava_bubbles = []
        self.birds = []
        self.falling_platforms = []
        self.axes = []
        self.firebars = []

        # Create background, fluid, and player
        self.bg = Background(background_image)
        self.fluid = Fluid(sprite_sheet, fluid_type)
        self.player = Player(player_sprite_sheet, self.display, (TILESIZE, TILESIZE * 19), self)

        # Create UI
        self.ui = UI(sprite_sheet, player_sprite_sheet, player_data)
        
        # set level states to false
        self.completed = False
        self.reset = False
        self.exited = False

        # Read data from csv file to initialize entities and put them in relevant list
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if col == SS_DIC.get("spider"):
                    spider = Spider((x * TILESIZE, y * TILESIZE), sprite_sheet, self.player)
                    self.damage_tiles.append(spider)
                    self.spiders.append(spider)
                elif col[:2] == SS_DIC.get("buzzsaw"):
                    path = buzzsaw_path_dict.get(col.split(":")[1])
                    buzzsaw = Buzzsaw((x * TILESIZE, y * TILESIZE), sprite_sheet, path)
                    self.damage_tiles.append(buzzsaw)
                    self.buzzsaws.append(buzzsaw)
                elif col == SS_DIC.get("fish"):
                    fish = Fish((x * TILESIZE, y * TILESIZE), sprite_sheet)
                    self.damage_tiles.append(fish)
                    self.fish.append(fish)
                elif col == SS_DIC.get("lavabubble"):
                    path = [pygame.math.Vector2(0, -7)]
                    lava_bubble = LavaBubble((x * TILESIZE, y * TILESIZE), sprite_sheet, path, 2)
                    self.damage_tiles.append(lava_bubble)
                    self.lava_bubbles.append(lava_bubble)
                elif col == SS_DIC.get("bird"):
                    bird = Bird((x * TILESIZE, y * TILESIZE), sprite_sheet, self.player)
                    self.damage_tiles.append(bird)
                    self.birds.append(bird)
                elif col == SS_DIC.get("falling_platform"):
                    falling_platform = FallingPlatform((x * TILESIZE, y * TILESIZE), sprite_sheet)
                    self.falling_platforms.append(falling_platform)
                    self.collision_tiles.append(falling_platform)
                elif col == SS_DIC.get("firebar"):
                    firebar = FireBar((x * TILESIZE, y * TILESIZE), sprite_sheet, self.damage_tiles)
                    self.firebars.append(firebar)
                    self.collision_tiles.append(firebar)
                elif col == SS_DIC.get("end_goal"):
                    self.end_goal = EndGoal((x * TILESIZE, y * TILESIZE), sprite_sheet)
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
        self.camera = Camera(self.player, TILESIZE, right_border)

    def update_level(self, dt, player_data):
        self.camera.scroll()
        self.player.update(dt, self.collision_tiles, self.damage_tiles, self.one_way_collision_tiles, self.end_goal, player_data)

        # Update falling platforms within boundaries
        for falling_platform in self.falling_platforms:
            if self.within_update_boundary(falling_platform):
                falling_platform.update(dt)

        # Update spiders within boundaries
        for spider in self.spiders:
            if self.within_update_boundary(spider):
                spider.update(self.collision_tiles, self.empty_tiles, self.one_way_collision_tiles, dt)

        # Update buzzsaws within boundaries
        for buzzsaw in self.buzzsaws:
            if self.within_update_boundary(buzzsaw):
                buzzsaw.update(dt)

        # Update axes within boundaries
        for axe in self.axes:
            if self.within_update_boundary(axe):
                axe.update(dt)

        # Update lava bubbles within boundaries
        for lava_bubble in self.lava_bubbles:
            if self.within_update_boundary(lava_bubble):
                lava_bubble.update(dt)

        for fish in self.fish:
            if self.within_update_boundary(fish):
                fish.update(dt)

        # Update birds within boundaries
        for bird in self.birds:
            if self.within_update_boundary(bird):
                bird.update(self.collision_tiles, dt)
        
        for firebar in self.firebars:
            if self.within_update_boundary(firebar):
                firebar.update(dt)

        # Update fluid within boundaries
        self.fluid.update()

        # Draw everything
        self.draw()

    def draw(self):
        # Draw background
        self.display.fill((255, 255, 255))
        self.bg.draw(self.camera, self.display)

        # Draw tiles within boundaries
        for tile in self.layer_one_tiles:
            if self.within_update_boundary(tile):
                tile.draw(self.display, self.camera)

        # Draw falling platforms within boundaries
        for falling_platform in self.falling_platforms:
            if self.within_update_boundary(falling_platform):
                falling_platform.draw(self.display, self.camera)

        # Draw player
        self.player.draw(self.camera)

        # Draw spiders within boundaries
        for spider in self.spiders:
            if self.within_update_boundary(spider):
                spider.draw(self.display, self.camera)

        # Draw buzzsaws within boundaries
        for buzzsaw in self.buzzsaws:
            if self.within_update_boundary(buzzsaw):
                buzzsaw.draw(self.display, self.camera)

        # Draw axes within boundaries
        for axe in self.axes:
            if self.within_update_boundary(axe):
                axe.draw(self.display, self.camera)

        # Draw lava bubbles within boundaries
        for lava_bubble in self.lava_bubbles:
            if self.within_update_boundary(lava_bubble):
                lava_bubble.draw(self.display, self.camera)

        for fish in self.fish:
            if self.within_update_boundary(fish):
                fish.draw(self.display, self.camera)

        # Draw birds within boundaries
        for bird in self.birds:
            if self.within_update_boundary(bird):
                bird.draw(self.display, self.camera)
        
        for firebar in self.firebars:
            if self.within_update_boundary(firebar):
                firebar.draw(self.display, self.camera)
        
        # Draw end goal within boundaries
        if self.within_update_boundary(self.end_goal):
            self.end_goal.draw(self.display, self.camera)

        # Draw fluid and UI
        self.fluid.draw(self.display, self.camera)
        self.ui.draw(self.display)
    
    # Determines if an object is within the level update boundary which is based on the player's postion
    # If not in boundary it should not be drawn
    def within_update_boundary(self, item):
        boundary_length = INTERNAL_DISPLAY_WIDTH
        right_check = self.player.position.x + boundary_length > item.position.x
        left_check = self.player.position.x - boundary_length < item.position.x
        return right_check and left_check

    # Method is called when level is paused, displays pause menu with options inside a textbox
    def pause_level(self, window):
        font = pygame.font.SysFont("Arial", 32) 
        menu_items = ["Restart Level", "Exit Level"]
        selected_item = 0  # Start by selecting the first option

        # Calculate the size and position of the textbox
        box_width = INTERNAL_DISPLAY_WIDTH * (2/3)
        box_height = INTERNAL_DISPLAY_HEIGHT * (2/3)
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
                    elif event.key == pygame.K_1:
                        return
                    elif event.key == pygame.K_f:
                        # Toggle between windowed and full screen
                        current_mode = pygame.display.get_surface().get_flags()
                        if current_mode & pygame.FULLSCREEN:
                            # Switch to windowed mode
                            window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
                        else:
                            # Switch to full screen
                            window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
            # continue to draw everything
            self.draw()

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
            scaled_surface = pygame.transform.scale(self.display, window.get_size())
            window.blit(scaled_surface, (0, 0))
            pygame.display.flip()