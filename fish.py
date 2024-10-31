import pygame
import math
from settings import *
from utils import *
import queue

class Fish:
    def __init__(self, pos, sprite_sheet, path, speed):
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.start_y = self.position.y
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        
        self.image_bottom = sprite_sheet.get_sprite_from_id(259, SPRITE_SHEET_WIDTH)
        self.image_bottom.set_colorkey(BLACK)
        self.image_up = sprite_sheet.get_sprite_from_id(199, SPRITE_SHEET_WIDTH)
        self.image_up.set_colorkey(BLACK)
        
        self.image = pygame.Surface((TILESIZE, TILESIZE * 2), pygame.SRCALPHA)
        self.image.blit(self.image_up, (0, 0))
        self.image.blit(self.image_bottom, (0, TILESIZE))
        self.rect_draw = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))

        self.arc_amplitude = 100
        self.arc_frequency = 0.03
        self.velocity = -1
        self.time = 0

    def update(self, dt):
        self.move(dt)

    def move(self, dt):
        self.rect.x += self.velocity * dt
        self.rect_draw.x += self.velocity * dt
        self.rect.y = self.start_y - abs(int(self.arc_amplitude * math.sin(self.arc_frequency * self.time)))
        self.rect_draw.y = self.start_y - abs(int(self.arc_amplitude * math.sin(self.arc_frequency * self.time))) - TILESIZE
        self.time += dt

        
    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect_draw.x - camera.offset.x, self.rect_draw.y - camera.offset.y))

