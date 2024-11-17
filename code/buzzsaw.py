import pygame
import math
from settings import *
from utils import *

# Class for buzzsaw that moves along a defined path and damages the player
class Buzzsaw:
    def __init__(self, pos, sprite_sheet, path):
        # Retrieve the sprite images for the buzzsaw's four corners from the sprite sheet
        image_topleft = sprite_sheet.get_sprite_from_id(15, SPRITE_SHEET_WIDTH)
        image_topright = sprite_sheet.get_sprite_from_id(16, SPRITE_SHEET_WIDTH)
        image_bottomleft = sprite_sheet.get_sprite_from_id(75, SPRITE_SHEET_WIDTH)
        image_bottomright = sprite_sheet.get_sprite_from_id(76, SPRITE_SHEET_WIDTH)
        
        # Create the surface for the buzzsaw and assemble it from the corner images
        self.image = pygame.Surface((TILESIZE * 2, TILESIZE * 2), pygame.SRCALPHA)
        self.image.blit(image_topleft, (0, 0))
        self.image.blit(image_topright, (TILESIZE, 0))
        self.image.blit(image_bottomright, (TILESIZE, TILESIZE))
        self.image.blit(image_bottomleft, (0, TILESIZE))
        self.image.set_colorkey(BLACK)  # Set transparent color to black
        
        # Copy the image for drawing
        self.image_draw = self.image.copy()
        
        # Set the position and velocity of the buzzsaw, using a vector for movement
        self.position = pygame.math.Vector2(pos[0] + TILESIZE, pos[1] + TILESIZE)
        self.velocity = pygame.math.Vector2(0, 0)
        
        # Define the rectangle for collision detection, centered on the position
        self.rect = self.image.get_rect(center=self.position)
        self.rect_draw = self.rect  # Draw rectangle

        # Initialize the rotation angle to 0
        self.angle = 0
        
        # Define the path and movement speed
        self.path = path
        self.speed = 1
        self.path_index = 0  # Start at the first path point
        self.previous_pos = pygame.math.Vector2(self.position.x, self.position.y)

    def draw(self, surface, camera):
        # Draw the buzzsaw on the surface, adjusting for the camera's offset
        surface.blit(self.image_draw, (self.rect_draw.x - camera.offset.x, self.rect_draw.y - camera.offset.y))

    def update(self, dt):
        # Update the buzzsaw's animation and movement
        self.animate()
        self.move(dt)

    def animate(self):
        # Increment the rotation angle by 3 degrees per frame
        self.angle += 3
        if self.angle >= 360:
            self.angle = 0  # Reset the angle to 0 after a full rotation

        # Rotate the image and smooth scale it to maintain its size during rotation
        self.image_draw = pygame.transform.rotate(self.image, self.angle)
        self.image_draw = pygame.transform.smoothscale(self.image_draw, (self.image_draw.get_width(), self.image_draw.get_height()))
        
        # Reset the transparent color for the rotated image
        self.image_draw.set_colorkey(BLACK)

        # Update the rectangle to reflect the rotated image's center
        self.rect_draw = self.image_draw.get_rect(center=self.image.get_rect(center=(self.position.x, self.position.y)).center)
        
    def move(self, dt):
        # Get the next move direction from the path
        next_move = self.path[self.path_index]
        
        # Calculate the target position based on the next move and the tile size
        target = pygame.math.Vector2(
            self.previous_pos.x + (next_move.x * (self.speed / abs(self.speed)) * TILESIZE),
            self.previous_pos.y + (next_move.y * (self.speed / abs(self.speed)) * TILESIZE)
        )

        # Normalize the next move vector for consistent movement
        next_move = next_move.normalize()

        # Update the current position based on the speed and delta time (dt)
        self.position.x += next_move.x * self.speed * dt
        self.position.y += next_move.y * self.speed * dt

        # Update the rectangle's center to match the new position
        self.rect.center = self.position

        # Calculate the difference between the target and current position
        target_x_diff = target.x - self.position.x
        target_y_diff = target.y - self.position.y

        # Check if the buzzsaw is close enough to the target position to proceed
        if abs(target_x_diff) < 1 and abs(target_y_diff) < 1:
            self.path_index += 1
            self.previous_pos = target
            
            # If we've reached the end of the path, reverse direction and reset path index
            if self.path_index >= len(self.path):
                self.path_index = 0
                self.speed *= -1  # Reverse the movement direction



