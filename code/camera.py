import pygame
from settings import *

# Camera class to determine what should be drawn on screen and where
class Camera:
    def __init__(self, player, left_border, right_border):
        # Initialize the camera with the player and the left/right borders of the world
        self.player = player
        self.left_border = left_border  # Left boundary for camera scrolling
        self.right_border = right_border  # Right boundary for camera scrolling
        
        # Initialize the offset vectors for the camera's position (used to scroll the world)
        self.offset = pygame.math.Vector2(0, 0)  # Whole number offset for rendering
        self.offset_float = pygame.math.Vector2(0, 0)  # Floating-point offset for smoother scrolling
        
        # CONST is used to calculate the initial offset to center the player in the display
        # It sets the camera to initially be at the player’s position, adjusting for display size
        self.CONST = pygame.math.Vector2(-INTERNAL_DISPLAY_WIDTH // 2 + player.rect.w // 2, -INTERNAL_DISPLAY_HEIGHT // 4)
        
        # Set the camera's y offset to match the initial vertical offset based on CONST
        self.offset_float.y = -self.CONST.y

    def scroll(self):
        # The camera follows the player along the x-axis, while respecting the left and right borders
        # Adjust the x-offset to follow the player’s position, accounting for the CONST horizontal offset
        self.offset_float.x += (self.player.rect.x - self.offset_float.x + self.CONST.x)
        
        # Update the integer offset for rendering based on the floating-point offset
        self.offset.x, self.offset.y = self.offset_float.x, self.offset_float.y
        
        # Constrain the x-offset within the defined left and right borders to prevent the camera from going out of bounds
        self.offset.x = max(self.left_border, self.offset.x)  # Ensure the camera doesn't go beyond the left border
        self.offset.x = min(self.offset.x, self.right_border)  # Ensure the camera doesn't go beyond the right border