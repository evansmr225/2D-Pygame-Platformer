import pygame
import math
from settings import *
from utils import *
import queue

# Draws a fluid over all other tiles on the screen and moves it
class Fluid:
    def __init__(self, sprite_sheet, fluid_type):
        self.image_list = []
        # get top and bottom images for fluid and put them in list, the type of image depends on the fluid_type which is a string
        for index in range(len(SS_DIC.get(fluid_type + "_top"))):
            image = pygame.Surface((TILESIZE, TILESIZE * 2))
            image_top = sprite_sheet.get_sprite_from_id(int(SS_DIC.get(fluid_type + "_top")[index]), SPRITE_SHEET_WIDTH)
            image_bottom = sprite_sheet.get_sprite_from_id(int(SS_DIC.get(fluid_type + "_bottom")[index]), SPRITE_SHEET_WIDTH)
            image.blit(image_top, (0, 0))
            image.blit(image_bottom, (0, TILESIZE))
            image.set_colorkey(BLACK)
            self.image_list.append(image)

        self.animation_index = 0
    
    def draw(self, surface, camera):
        # Calculate how many tiles to draw based on the camera's right border
        number_of_tiles = camera.right_border
        for index in range(number_of_tiles):
            # Cycle through fluid images in the list and draw them on the screen with proper offset
            surface.blit(self.image_list[index % len(self.image_list)], (TILESIZE * index - camera.offset.x, INTERNAL_DISPLAY_HEIGHT - camera.offset.y + TILESIZE * 3))

    def update(self):
        # Update the fluid's animation: every other frame, cycle the images
        if self.animation_index % (TARGET_FPS // 30) == 0:
            # Shift the images in the list, creating the illusion of moving fluid
            self.image_list = self.image_list[1:] + [self.image_list[0]]

        self.animation_index += 1
        if self.animation_index == TARGET_FPS:
            self.animation_index = 0
         


