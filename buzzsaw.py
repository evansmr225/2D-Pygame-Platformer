import pygame
import math
from settings import *
from utils import *
import numpy

class Buzzsaw:
    def __init__(self, pos, sprite_sheet, path):
        image_topleft = sprite_sheet.get_sprite_from_id(15, SPRITE_SHEET_WIDTH)
        image_topright = sprite_sheet.get_sprite_from_id(16, SPRITE_SHEET_WIDTH)
        image_bottomleft = sprite_sheet.get_sprite_from_id(75, SPRITE_SHEET_WIDTH)
        image_bottomright = sprite_sheet.get_sprite_from_id(76, SPRITE_SHEET_WIDTH)
        self.image = pygame.Surface((TILESIZE * 2, TILESIZE * 2), pygame.SRCALPHA)
        self.image.blit(image_topleft, (0, 0))
        self.image.blit(image_topright, (TILESIZE, 0))
        self.image.blit(image_bottomright, (TILESIZE, TILESIZE))
        self.image.blit(image_bottomleft, (0, TILESIZE))
        self.image.set_colorkey(BLACK)
        self.image_draw = self.image.copy()
        self.position = pygame.math.Vector2(pos[0] + TILESIZE, pos[1] + TILESIZE)
        self.velocity = pygame.math.Vector2(0, 0)
        self.rect = self.image.get_rect(center = self.position)
        self.rect_draw = self.rect
        self.angle = 0
        
        self.path = path
        self.speed = 1
        self.path_index = 0
        self.previous_pos = pygame.math.Vector2(self.position.x, self.position.y)

    def draw(self, surface, camera):
        surface.blit(self.image_draw, (self.rect_draw.x - camera.offset.x, self.rect_draw.y - camera.offset.y))

    def update(self, dt):
        self.animate()
        self.move(dt)

    def animate(self):
        self.angle += 3  # Increment angle for rotation 
        if self.angle >= 360:
            self.angle = 0  # Reset angle to 0

        # Rotate image 
        self.image_draw = pygame.transform.rotate(self.image, self.angle)
        self.image_draw = pygame.transform.smoothscale(self.image_draw, (self.image_draw.get_width(), self.image_draw.get_height()))
        self.image_draw.set_colorkey(BLACK)
        self.rect_draw = self.image_draw.get_rect(center=self.image.get_rect(center=(self.position.x, self.position.y)).center)
        
    def move(self, dt):
        next_move = self.path[self.path_index]
        
        # Calculate the target position based on the next move and TILESIZE
        target = pygame.math.Vector2(
            self.previous_pos.x + (next_move.x * numpy.sign(self.speed) * TILESIZE),
            self.previous_pos.y + (next_move.y * numpy.sign(self.speed) * TILESIZE)
        )

        next_move = next_move.normalize()

        # Update the current position based on speed and delta time (dt)
        self.position.x += next_move.x * self.speed * dt
        self.position.y += next_move.y * self.speed * dt

        # Update the rectangle's center position
        self.rect.center = self.position

        # Calculate the differences between the target and current positions
        target_x_diff = target.x - self.position.x
        target_y_diff = target.y - self.position.y

        # Check if the object is close enough to the target position
        if abs(target_x_diff) < 1 and abs(target_y_diff) < 1:  # Adjust the threshold as needed
            self.path_index += 1
            self.previous_pos = target
            
            # Reset or reverse the path index if it exceeds the path length
            if self.path_index >= len(self.path):
                self.path_index = 0
                self.speed *= -1  # Reverse the direction if needed
        



