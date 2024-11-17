import pygame

# Class to represent a tile in the game world, inheriting from pygame's Sprite class
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        # Initialize the Tile object with an image and its position
        self.image = image  # The image representing the tile
        self.position = pygame.math.Vector2(x, y)  # Position of the tile as a Vector2
        self.rect = self.image.get_rect(topleft=(x, y))  # Create a rect to represent the tile's boundaries, positioned at (x, y)

    def draw(self, surface, camera):
        # Draw the tile on the given surface, considering the camera's offset
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))  # Render the tile on screen with camera offset