import pygame
from settings import *

class EndGoal:
    def __init__(self, pos, sprite_sheet):
        self.image = sprite_sheet.get_sprite_from_id(14, SPRITE_SHEET_WIDTH)
        self.image.set_colorkey(BLACK)
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))