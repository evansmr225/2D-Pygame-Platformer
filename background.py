import pygame
from settings import *

class Background:
    def __init__(self, background_image):
        self.image = pygame.transform.scale(background_image, (INTERNAL_DISPLAY_WIDTH, INTERNAL_DISPLAY_HEIGHT))
        self.parallax_factor = 0.5
        self.image_width = background_image.get_width()

    def draw(self, camera, display):
        x_value = -(camera.offset.x * self.parallax_factor) % self.image_width
        display.blit(self.image, (x_value, 0))
        display.blit(self.image, (x_value - self.image_width, 0))