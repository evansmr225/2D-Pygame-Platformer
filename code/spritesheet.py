import pygame
from settings import *

# Class to create a spritesheet object which can return tiled sprites from it
class Spritesheet:
    def __init__(self, filename):
        # Initialize the spritesheet by loading the image file
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()  # Load the image with transparency

    def get_sprite(self, x, y, w, h):
        # Extract a specific sprite from the spritesheet based on given coordinates and dimensions
        sprite = pygame.Surface((w, h))  # Create a new surface for the sprite
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))  # Copy the relevant section from the spritesheet
        return sprite  # Return the cropped sprite

    def get_sprite_from_id(self, id, image_width):
        # Calculate the x and y coordinates based on sprite id and image width
        y = (id // (image_width // TILESIZE)) * TILESIZE  # Determine the y coordinate of the sprite in the spritesheet
        x = (id % (image_width // TILESIZE)) * TILESIZE  # Determine the x coordinate of the sprite in the spritesheet
        # Return the sprite extracted from the calculated coordinates
        return self.get_sprite(x, y, TILESIZE, TILESIZE)
