import pygame
import random
import math
from settings import *
from utils import *
from enum import Enum

class BirdState(Enum):
    PATROL = 0
    DIVE = 1
    RECOVER = 2

class Bird:
    def __init__(self, pos, sprite_sheet, player):
        self.position, self.velocity = pygame.math.Vector2(pos), pygame.math.Vector2(0, 0) 
        self.gravity = 0.5
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        self.is_facing_left = False
        self.player = player
        self.init_images(sprite_sheet)
        self.animation_count = 0
        self.state = BirdState.PATROL
        
        self.start_pos = pygame.math.Vector2(pos)
        self.target = pygame.math.Vector2(0, 0)
        self.arc_height = 2
        self.max_velocity = 1.5
        self.patrol_radius = 3
        
        self.animate()

    def init_images(self, sprite_sheet):
        image_1 = sprite_sheet.get_sprite_from_id(78, SPRITE_SHEET_WIDTH)
        image_1.set_colorkey(BLACK)
        image_2 = sprite_sheet.get_sprite_from_id(81, SPRITE_SHEET_WIDTH)
        image_2.set_colorkey(BLACK)
        image_3 = sprite_sheet.get_sprite_from_id(84, SPRITE_SHEET_WIDTH)
        image_3.set_colorkey(BLACK)

        
        self.images_left = [image_1, image_2, image_3]

        self.images_right = []
        for image in self.images_left:
            image_right = pygame.transform.flip(image, True, False)
            self.images_right.append(image_right)

    def animate(self):
        if self.is_facing_left:
            self.image = self.images_left[(self.animation_count // len(self.images_left)) % len(self.images_left)]
        else:
            self.image = self.images_right[(self.animation_count // len(self.images_right)) % len(self.images_right)]
        self.animation_count += 1
        if self.animation_count == 60:
            self.animation_count = 0

    def checkCollisionsx(self, collision_tiles):
        collisions = self.get_collisions(collision_tiles, self.rect)
        for tile in collisions:
            if self.velocity.x > 0 and tile.rect.x >= self.rect.x:
                self.position.x = tile.rect.left - self.rect.w
                self.rect.x = self.position.x
                self.is_facing_left = not self.is_facing_left
                
                if self.state == BirdState.DIVE:
                    self.state == BirdState.RECOVER
                    self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                    self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
                    self.velocity.x = 0
                    self.velocity.y = 0
            elif self.velocity.x < 0 and self.is_facing_left and tile.rect.x <= self.rect.x:
                self.position.x = tile.rect.right
                self.rect.x = self.position.x
                self.is_facing_left = not self.is_facing_left
                
                if self.state == BirdState.DIVE:
                    self.state == BirdState.RECOVER
                    self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                    self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
                    self.velocity.x = 0
                    self.velocity.y = 0

    def checkCollisionsy(self, collision_tiles):
        collisions = self.get_collisions(collision_tiles, self.rect)
        for tile in collisions:
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.position.y = tile.rect.top - TILESIZE
                self.rect.bottom = self.position.y

                self.state = BirdState.RECOVER
                self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                self.target = pygame.math.Vector2(self.position.x, self.position.y - (3 * TILESIZE))
                self.velocity.x = 0
                self.velocity.y = 0
            elif self.velocity.y < 0:
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.rect.h
                self.rect.bottom = self.position.y
                
                self.state = BirdState.PATROL
                self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                self.velocity.x = 0
                self.velocity.y = 0

    def calculate_movement(self, dt):
        #print(f"Bird Position: X={self.rect.x}, Y={self.rect.y}, State={self.state.name}")
        if self.state == BirdState.PATROL:
            self.patrol()
        elif self.state == BirdState.DIVE:
            self.dive(dt)
        elif self.state == BirdState.RECOVER:
            self.recover(dt)

    def patrol(self):
         # Set target positions based on direction
        if self.is_facing_left:
            self.target.x = self.start_pos.x - self.patrol_radius * TILESIZE
        else:
            self.target.x = self.start_pos.x + self.patrol_radius * TILESIZE

        # Check if the current position exceeds the target boundary
        if self.position.x <= self.target.x and self.is_facing_left:
            self.is_facing_left = False  # Change direction
            self.velocity.x = self.max_velocity  # Move right
        elif self.position.x >= self.target.x and not self.is_facing_left:
            self.is_facing_left = True  # Change direction
            self.velocity.x = -self.max_velocity # Move left
        else:
            # If within bounds, continue moving in the current direction
            self.velocity.x = self.max_velocity if not self.is_facing_left else -self.max_velocity
        
        dive_zone_left = self.position.x - (TILESIZE * 3) if self.is_facing_left else self.position.x + (TILESIZE * 1)
        dive_zone_right = self.position.x - (TILESIZE * 1) if self.is_facing_left else self.position.x + (TILESIZE * 3)
        dive_zone_bottom = self.position.y + (TILESIZE * 3)
        dive_zone_top = self.position.y + (TILESIZE * 1)

        left_check = self.player.position.x >= dive_zone_left
        right_check = self.player.position.x <= dive_zone_right
        bottom_check = self.player.position.y <= dive_zone_bottom
        top_check = self.player.position.y >= dive_zone_top

        if not (left_check and right_check and top_check and bottom_check):
            return

        if random.random() < 0.5:
            self.state = BirdState.DIVE
            self.velocity.x = 0
            self.velocity.y = 0
            self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
            self.target = pygame.math.Vector2(self.player.position.x, self.player.position.y)

    # def dive(self, dt):
    #     if not self.is_facing_left and self.rect.x < self.target.x:
    #         self.velocity.x += self.acceleration.x * dt
    #         self.velocity.x = min(self.velocity.x, self.max_velocity)
    #     elif self.is_facing_left and self.rect.x > self.target.x:
    #         self.velocity.x -= self.acceleration.x * dt
    #         self.velocity.x = max(self.velocity.x, -self.max_velocity)
    #     else:
    #         self.state = BirdState.RECOVER
    #         self.start_pos = self.position
    #         self.target = pygame.math.Vector2(0, self.position.y - 3)
    #         self.velocity.x = 0
    #         self.velocity.y = 0
    #         return

    #     progress = (self.rect.x - self.start_pos.x) / (self.target.x - self.start_pos.x)

    #     desired_y = self.start_pos.y + (progress * (self.target.y - self.start_pos.y)) - math.sin(progress * math.pi) * self.arc_height
    #     self.velocity.y = (desired_y - self.rect.y) * self.acceleration.y * dt

    def dive(self, dt):
        # Calculate the difference between the current position and the target
        diff_x = self.target.x - self.rect.x
        diff_y = self.target.y - self.rect.y

        # Calculate the angle and direction (normalized direction vector)
        distance = math.hypot(diff_x, diff_y)  # Get the straight-line distance to the target

        if distance > 0:  # To avoid division by zero
            direction_x = diff_x / distance
            direction_y = diff_y / distance
        else:
            direction_x = 0
            direction_y = 0

        # Set velocity based on the direction and the bird's speed
        self.velocity.x = direction_x * self.max_velocity
        self.velocity.y = direction_y * self.max_velocity

        # Check if bird has reached the target (or is very close)
        if distance < 1:  # Tolerance to stop the bird when it's near the target
            self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
            self.state = BirdState.RECOVER  # Switch to another state if needed

    def recover(self, dt):
        self.velocity.y = -self.max_velocity

        if self.rect.y <= self.target.y:
            self.state = BirdState.PATROL
            self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
            self.velocity.x = 0
            self.velocity.y = 0

    def horizontal_movement(self, dt):
        self.position.x += self.velocity.x * dt
        self.rect.x = self.position.x

    def vertical_movement(self, dt):
        self.position.y += self.velocity.y * dt
        self.rect.y = self.position.y
            
    def get_collisions(self, tiles, rect):
        collisions = []
        for tile in tiles:
            if tile.rect.colliderect(rect):
                collisions.append(tile)
        return collisions
    
    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
    
    def update(self, collision_tiles, dt):
        self.calculate_movement(dt)
        self.horizontal_movement(dt)
        self.checkCollisionsx(collision_tiles)
        self.vertical_movement(dt)
        self.checkCollisionsy(collision_tiles)
        self.animate()