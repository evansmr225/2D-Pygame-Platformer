import pygame
from settings import *
from utils import *
import os
import math

class FireBar:
    # Inner Ball class represents each fireball
    class Ball:
        def __init__(self, pivot_pos, radius, angle):
            # Load the image for the fireball
            self.image = pygame.image.load(resource_path(os.path.join("assets", "images", "fireball.png"))).convert_alpha()
            self.draw_image = self.image.copy()  # Store a copy for later rotation
            self.radius = radius  # Set the radius from the pivot
            # Calculate initial position of the ball using polar coordinates (radius, angle)
            x = pivot_pos.x + radius + math.cos(angle)
            y = pivot_pos.y + radius + math.sin(angle)
            # Create the rectangle for collision detection
            self.rect = self.image.get_rect(topleft=(x, y))

    def __init__(self, pos, sprite_sheet, damage_tiles, number_of_balls=3):
        # Set the position of the firebar's pivot
        self.position = pygame.math.Vector2(pos[0], pos[1])

        # Load the sprite for the pivot (center of the firebar) from the sprite sheet
        self.pivot_image = sprite_sheet.get_sprite_from_id(2, SPRITE_SHEET_WIDTH)
        self.pivot_image.set_colorkey(BLACK)  # Set transparency color to black
        # Create a rectangle for the pivot's collision detection
        self.rect = self.pivot_image.get_rect(topleft=self.position)

        # Set rotation speed and angle for each fireball
        self.speed = 0.05
        self.angle = 0
        
        # Create a list to hold the fireball objects
        self.balls = []
        for i in range(number_of_balls):
            # For each ball, create a new Ball object with increasing radius
            ball = self.Ball(self.position, (i + 1) * TILESIZE, self.angle)
            self.balls.append(ball)
            # Add the ball to the damage tiles list for collision detection
            damage_tiles.append(ball)

    def update(self, dt):
        # Update the angle of rotation for the firebar
        self.angle += self.speed * dt
        # Update the position and rotation of each fireball based on the new angle
        for ball in self.balls:
            # Calculate new position using polar coordinates
            x = self.position.x + ball.radius * math.cos(self.angle)
            y = self.position.y + ball.radius * math.sin(self.angle)
            # Update the fireball's rectangle position
            ball.rect.x = x
            ball.rect.y = y
            # Rotate the fireball image based on the current angle
            ball.draw_image = pygame.transform.rotate(ball.image, self.angle * 50)

    def draw(self, surface, camera):
        # Draw the pivot on the screen with camera offset
        surface.blit(self.pivot_image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
        # Draw each fireball, accounting for camera offset
        for ball in self.balls:
            surface.blit(ball.draw_image, (ball.rect.x - camera.offset.x, ball.rect.y - camera.offset.y))
