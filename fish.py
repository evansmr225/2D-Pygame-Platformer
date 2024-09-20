import pygame
import math
from settings import *
from utils import *
import queue
import numpy

class Fish:
    def __init__(self, pos, sprite_sheet, path, speed):
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        image_top = sprite_sheet.get_sprite_from_id(199, SPRITE_SHEET_WIDTH)
        image_bottom = sprite_sheet.get_sprite_from_id(259, SPRITE_SHEET_WIDTH)
        self.image_up = pygame.Surface((TILESIZE, TILESIZE * 2))
        self.image_up.set_colorkey(BLACK)
        self.image_up.blit(image_top, (0, 0))
        self.image_up.blit(image_bottom, (0, TILESIZE))
        self.image_down = pygame.transform.rotate(self.image_up, 180)
        self.image_down = pygame.transform.flip(self.image_up, False, True)
        self.image = self.image_up
        self.rect_draw = self.image_up.get_rect(topleft = (pos[0], pos[1] - TILESIZE))

        self.path = path
        self.speed = speed
        self.path_index = 0
        self.previous_pos = pygame.math.Vector2(self.position.x, self.position.y)

    def update(self, dt):
        self.move(dt)

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
        self.rect.topleft = self.position
        self.rect_draw.topleft = self.position

        # Calculate the differences between the target and current positions
        target_x_diff = target.x - self.position.x
        target_y_diff = target.y - self.position.y

        # Check if the object is close enough to the target position
        if abs(target_x_diff) < TILESIZE // 2 and abs(target_y_diff) < TILESIZE // 2:  # Adjust the threshold as needed
            self.path_index += 1
            self.previous_pos = target
            
            # Reset or reverse the path index if it exceeds the path length
            if self.path_index >= len(self.path):
                self.path_index = 0
                self.speed *= -1  # Reverse the direction if needed
                self.image = self.image_down if self.image == self.image_up else self.image_up
        
    
    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect_draw.x - camera.offset.x, self.rect_draw.y - camera.offset.y))

