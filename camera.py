import pygame
from settings import *

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
        self.offset.x, self.offset.y = self.offset_float.x, self.offset_float.y
        self.offset.x = max(self.left_border, self.offset.x)
        self.offset.x = min(self.offset.x, self.right_border)