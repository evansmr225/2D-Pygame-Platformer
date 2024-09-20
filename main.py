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
    def __init__(self, display):
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

    def update_level(self, dt):
        # update everything
        self.camera.scroll()
        self.player.update(dt, self.collision_tiles, self.damage_tiles, self.one_way_collision_tiles)
        for spider in self.spiders: spider.update(self.collision_tiles, self.empty_tiles, self.one_way_collision_tiles, dt)
        for buzzsaw in self.buzzsaws: buzzsaw.update(dt)
        for lava_bubble in self.lava_bubbles: lava_bubble.update(dt)
        self.fluid.update()
        
        # draw everything
        #displays the background
        self.display.blit(self.bg, (0, 0))
        for tile in self.layer_one_tiles: tile.draw(self.display, self.camera)
        self.player.draw(self.camera)
        for spider in self.spiders: spider.draw(self.display, self.camera)
        for buzzsaw in self.buzzsaws: buzzsaw.draw(self.display, self.camera)
        for lava_bubble in self.lava_bubbles: lava_bubble.draw(self.display, self.camera)
        self.fluid.draw(self.display, self.camera)

    def reset(self):
        self.__init__(self.display)

def main():
    pygame.init()

    internal_width = 320
    internal_height = 240
    internal_surface = pygame.Surface((internal_width, internal_height))

    window_size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    window = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
    pygame.display.set_caption("Basic Pygame Window")
    clock = pygame.time.Clock()
    level = Level(internal_surface)

    running = True
    while running:
        dt = clock.tick(60) *.001 * TARGET_FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    level.player.left_key, level.player.facing_left = True, True
                if event.key == pygame.K_RIGHT:
                    level.player.right_key, level.player.facing_left = True, False
                if event.key == pygame.K_SPACE:
                    level.player.jump()
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
        level.update_level(dt)
        
        scaled_surface = pygame.transform.scale(internal_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        window.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


main()