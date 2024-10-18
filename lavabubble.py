import pygame
import math
from settings import *
from utils import *

class LavaBubble:
    def __init__(self, pos, sprite_sheet, path, speed):
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        self.image_up_1 = sprite_sheet.get_sprite_from_id(271, SPRITE_SHEET_WIDTH)
        self.image_up_1.set_colorkey(BLACK)
        self.image_down_1 = pygame.transform.rotate(self.image_up_1, 180)
        self.image_up_2 = sprite_sheet.get_sprite_from_id(274, SPRITE_SHEET_WIDTH)
        self.image_up_2.set_colorkey(BLACK)
        self.image_down_2 = pygame.transform.rotate(self.image_up_2, 180)
        self.image = self.image_up_1

        self.animation_count = 0
        self.path = path
        self.speed = speed
        self.path_index = 0
        self.previous_pos = pygame.math.Vector2(self.position.x, self.position.y)

    def update(self, dt):
        self.move(dt)
        self.animate()

    def move(self, dt):
        next_move = self.path[self.path_index]
        
        # Calculate the target position based on the next move and TILESIZE
        target = pygame.math.Vector2(
            self.previous_pos.x + (next_move.x * (self.speed / abs(self.speed)) * TILESIZE),
            self.previous_pos.y + (next_move.y * (self.speed / abs(self.speed)) * TILESIZE)
        )

        next_move = next_move.normalize()

        # Update the current position based on speed and delta time (dt)
        self.position.x += next_move.x * self.speed * dt
        self.position.y += next_move.y * self.speed * dt

        # Update the rectangle's center position
        self.rect.topleft = self.position

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
                self.speed *= -1

    def animate(self):
        if self.animation_count < 30 and self.speed < 0:
            self.image = self.image_down_1
        elif self.animation_count >= 30 and self.speed < 0:
            self.image = self.image_down_2
        elif self.animation_count < 30 and self.speed >= 0:
            self.image = self.image_up_1
        elif self.animation_count >= 30 and self.speed >= 0:
            self.image = self.image_up_2

        self.animation_count += 1
        if self.animation_count == 60:
            self.animation_count = 0
        
    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))

