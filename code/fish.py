import pygame
import math
from settings import *
from utils import *
import queue

class Fish:
    def __init__(self, pos, sprite_sheet):
        # Initialize start position and create rect for collisions
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.start_y = self.position.y
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        
        # get top and bottom of fish sprites from sprite sheet
        image_bottom_1 = sprite_sheet.get_sprite_from_id(259, SPRITE_SHEET_WIDTH)
        image_bottom_1.set_colorkey(BLACK)
        image_up_1 = sprite_sheet.get_sprite_from_id(199, SPRITE_SHEET_WIDTH)
        image_up_1.set_colorkey(BLACK)
        image_bottom_2 = sprite_sheet.get_sprite_from_id(262, SPRITE_SHEET_WIDTH)
        image_bottom_2.set_colorkey(BLACK)
        image_up_2 = sprite_sheet.get_sprite_from_id(202, SPRITE_SHEET_WIDTH)
        image_up_2.set_colorkey(BLACK)
        
        # create fish image 1
        self.image_1 = pygame.Surface((TILESIZE, TILESIZE * 2), pygame.SRCALPHA)
        self.image_1.blit(image_up_1, (0, 0))
        self.image_1.blit(image_bottom_1, (0, TILESIZE))

        # create fish image 2
        self.image_2 = pygame.Surface((TILESIZE, TILESIZE * 2), pygame.SRCALPHA)
        self.image_2.blit(image_up_2, (0, 0))
        self.image_2.blit(image_bottom_2, (0, TILESIZE))

        # set current image to fish image 1
        self.image = self.image_1
        # create rect for drawing the fish since it has a top and bottom part
        self.rect_draw = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))

        # keeps track of frames for animation purposes
        self.animation_index = 0

        # variables of the arc that the fish travels in
        self.arc_amplitude = 100
        self.arc_frequency = 0.03
        self.velocity = -1
        self.time = 0

    def update(self, dt):
        self.move(dt)
        self.animate()

    def move(self, dt):
        # moves fish in sine wave
        self.rect.x += self.velocity * dt
        self.rect_draw.x += self.velocity * dt
        self.position.x = self.rect.x
        self.rect.y = self.start_y - abs(int(self.arc_amplitude * math.sin(self.arc_frequency * self.time)))
        self.rect_draw.y = self.start_y - abs(int(self.arc_amplitude * math.sin(self.arc_frequency * self.time))) - TILESIZE
        self.position.y = self.rect.y
        # updates time to make fish move along sine wave
        self.time += dt
        
        
    # animate fish
    def animate(self):
        self.animation_index += 1
        if self.animation_index == 60:
            self.animation_index = 0
        if self.animation_index < 30:
            self.image = self.image_1
        else:
            self.image = self.image_2

        self.animation_index += 1
        if self.animation_index == 60:
            self.animation_index = 0

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect_draw.x - camera.offset.x, self.rect_draw.y - camera.offset.y))

