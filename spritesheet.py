import pygame
from settings import *

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