import pygame
from settings import *

# User interface which draws images on top of everything else, includes player life data
class UI:
    def __init__(self, sprite_sheet, player_sprite_sheet, player_data):
        self.player_life_icon = player_sprite_sheet.get_sprite_from_id(13, 192)
        self.player_life_icon.set_colorkey(BLACK)
        self.font = pygame.font.SysFont("Verdana", 12)
        self.life_text = self.font.render(f": {player_data.lives}", True, WHITE)

    def draw(self, surface):
        surface.blit(self.player_life_icon, ((TILESIZE * 17), 0))
        surface.blit(self.life_text, ((TILESIZE * 18), 0))