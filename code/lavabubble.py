import pygame
import math
from settings import *
from utils import *

class LavaBubble:
    def __init__(self, pos, sprite_sheet, path, speed):
         # Initialize the LavaBubble's position and set up a rectangle for collision
        self.position = pygame.math.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        
        # Load the sprite images for the LavaBubble (upward and downward states)
        self.image_up_1 = sprite_sheet.get_sprite_from_id(271, SPRITE_SHEET_WIDTH)
        self.image_up_1.set_colorkey(BLACK)
        self.image_down_1 = pygame.transform.rotate(self.image_up_1, 180)
        self.image_up_2 = sprite_sheet.get_sprite_from_id(274, SPRITE_SHEET_WIDTH)
        self.image_up_2.set_colorkey(BLACK)
        self.image_down_2 = pygame.transform.rotate(self.image_up_2, 180)
        
        # Set initial image for the LavaBubble
        self.image = self.image_up_1
        
        # Initialize animation counter and movement parameters
        self.animation_count = 0
        self.path = path # Path the LavaBubble will follow (list of directions)
        self.speed = speed
        self.path_index = 0
        self.previous_pos = pygame.math.Vector2(self.position.x, self.position.y)

    def update(self, dt):
        self.move(dt)
        self.animate()

    def move(self, dt):
        # Get the next move from the path list
        next_move = self.path[self.path_index]
        
        # Calculate the target position based on the current direction and speed
        target = pygame.math.Vector2(
            self.previous_pos.x + (next_move.x * (self.speed / abs(self.speed)) * TILESIZE),
            self.previous_pos.y + (next_move.y * (self.speed / abs(self.speed)) * TILESIZE)
        )

        # Normalize the direction vector for smooth movement
        next_move = next_move.normalize()

        # Update the LavaBubble's position based on the speed and delta time (dt)
        self.position.x += next_move.x * self.speed * dt
        self.position.y += next_move.y * self.speed * dt

        # Update the rectangle's position for collision detection
        self.rect.topleft = self.position

        # Calculate the difference between the target and current position
        target_x_diff = target.x - self.position.x
        target_y_diff = target.y - self.position.y

        # Check if the LavaBubble has reached the target position
        if abs(target_x_diff) < TILESIZE // 2 and abs(target_y_diff) < TILESIZE // 2:
            # Move to the next path point and update the previous position
            self.path_index += 1
            self.previous_pos = target
            
            # If the path is complete, reverse direction and restart the path
            if self.path_index >= len(self.path):
                self.path_index = 0
                self.speed *= -1  # Reverse the speed to change direction

    def animate(self):
        # Cycle through the animation frames depending on the movement direction and time
        if self.animation_count < 30 and self.speed < 0:
            self.image = self.image_down_1  # Set downward image for upward speed
        elif self.animation_count >= 30 and self.speed < 0:
            self.image = self.image_down_2  # Second downward frame for upward speed
        elif self.animation_count < 30 and self.speed >= 0:
            self.image = self.image_up_1  # First upward frame for downward speed
        elif self.animation_count >= 30 and self.speed >= 0:
            self.image = self.image_up_2  # Second upward frame for downward speed

        # Increment the animation counter and reset it after 60 frames
        self.animation_count += 1
        if self.animation_count == 60:
            self.animation_count = 0
        
    def draw(self, surface, camera):
        # Draw the LavaBubble on the screen, adjusted by the camera's offset
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
    

    

