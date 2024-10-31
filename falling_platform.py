import pygame
from settings import *

class FallingPlatform:

    def __init__(self, pos, sprite_sheet):
        image_1 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')), SPRITE_SHEET_WIDTH) 
        image_2 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')) + 1, SPRITE_SHEET_WIDTH) 
        image_3 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')) + 2, SPRITE_SHEET_WIDTH) 
        self.image = pygame.Surface((TILESIZE * 3, TILESIZE), pygame.SRCALPHA)
        self.image.blit(image_1, (0, 0))
        self.image.blit(image_2, (TILESIZE, 0))
        self.image.blit(image_3, (TILESIZE * 2, 0))
        self.image.set_colorkey(BLACK)

        self.position = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(topleft = self.position)
        
        self.fall_timer = 120
        self.should_move = False
        self.velocity = pygame.math.Vector2(0, 0)
        self.falling_velocity = 3

    def player_collision_event(self):
        self.fall_timer -= 1
        
    def update(self, dt):
        if self.fall_timer <= 0:
            self.position.y += self.falling_velocity * dt
            self.rect.y = self.position.y

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))



