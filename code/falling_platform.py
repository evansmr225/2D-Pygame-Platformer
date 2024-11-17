import pygame
from settings import *

class FallingPlatform:
    def __init__(self, pos, sprite_sheet):
        # Retrieve three consecutive images from the sprite sheet to form the platform
        image_1 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')), SPRITE_SHEET_WIDTH)
        image_2 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')) + 1, SPRITE_SHEET_WIDTH)
        image_3 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('falling_platform')) + 2, SPRITE_SHEET_WIDTH)
        
        # Create a surface for the platform with the combined width of three tiles
        self.image = pygame.Surface((TILESIZE * 3, TILESIZE), pygame.SRCALPHA)
        
        # Blit the three images onto the surface to create the full platform
        self.image.blit(image_1, (0, 0))
        self.image.blit(image_2, (TILESIZE, 0))
        self.image.blit(image_3, (TILESIZE * 2, 0))
        
        # Set transparency for the platform's surface
        self.image.set_colorkey(BLACK)

        # Set the initial position of the platform and create a rectangle for collision detection
        self.position = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(topleft=self.position)
        
        # Initialize the fall timer, which determines how long the platform waits before falling
        self.fall_timer = 120  # Time before the platform starts falling (in frames)
        
        # Boolean flag to track if the platform should start falling
        self.should_move = False
        
        # Set the velocity and the falling speed of the platform
        self.velocity = pygame.math.Vector2(0, 0)
        self.falling_velocity = 3  # Speed at which the platform falls

    def player_collision_event(self):
        # When the player collides with the platform, reduce the fall timer
        self.fall_timer -= 1

    def update(self, dt):
        # If the fall timer has expired, make the platform fall
        if self.fall_timer <= 0:
            # Update the platform's vertical position by its falling velocity and delta time
            self.position.y += self.falling_velocity * dt
            self.rect.y = self.position.y  # Update the rectangle’s position to match the new platform position

    def draw(self, surface, camera):
        # Draw the platform on the screen, adjusting for camera offset
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))



