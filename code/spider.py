import pygame
import random
from settings import *
from utils import *

class Spider:
    def __init__(self, pos, sprite_sheet, player):
        # Initialize basic properties such as gravity, position, velocity, and acceleration
        self.gravity = .35
        self.position, self.velocity = pygame.math.Vector2(pos), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        # Set up the rectangular bounds (collision boxes) for the spider
        self.rect = pygame.Rect(self.position, (TILESIZE * 2, TILESIZE))
        self.bottom_rect = pygame.Rect((self.rect.x, self.rect.y + TILESIZE), (TILESIZE * 2, TILESIZE))
        # Initialize state variables for the spider
        self.is_facing_left = False
        self.on_ground = True
        self.player = player  # Reference to the player for interaction or behavior
        self.init_images(sprite_sheet)  # Initialize the spider's images from the sprite sheet
        self.animation_count = 0  # Counter for animation frames
        self.animate()  # Initial animation setup

    def init_images(self, sprite_sheet):
        # Extract images for the spider's animation (facing left and right)
        left_spider_1 = sprite_sheet.get_sprite_from_id(426, SPRITE_SHEET_WIDTH)
        left_spider_1.set_colorkey(BLACK)  # Remove black color from the sprite
        right_spider_1 = sprite_sheet.get_sprite_from_id(427, SPRITE_SHEET_WIDTH)
        right_spider_1.set_colorkey(BLACK)  # Remove black color from the sprite
        image_1 = (left_spider_1, right_spider_1)
        
        # Similarly load other animation frames
        left_spider_2 = sprite_sheet.get_sprite_from_id(430, SPRITE_SHEET_WIDTH)
        left_spider_2.set_colorkey(BLACK)
        right_spider_2 = sprite_sheet.get_sprite_from_id(431, SPRITE_SHEET_WIDTH)
        right_spider_2.set_colorkey(BLACK)
        image_2 = (left_spider_2, right_spider_2)

        left_spider_3 = sprite_sheet.get_sprite_from_id(434, SPRITE_SHEET_WIDTH)
        left_spider_3.set_colorkey(BLACK)
        right_spider_3 = sprite_sheet.get_sprite_from_id(435, SPRITE_SHEET_WIDTH)
        right_spider_3.set_colorkey(BLACK)
        image_3 = (left_spider_3, right_spider_3)
        
        # Store the frames for both left-facing and right-facing spider animations
        self.images_left = [image_1, image_2, image_3]

        self.images_right = []
        for image in self.images_left:
            image_right_1 = pygame.transform.flip(image[1], True, False)
            image_right_2 = pygame.transform.flip(image[0], True, False)
            image_right = (image_right_1, image_right_2)
            self.images_right.append(image_right)

    def animate(self):
        # Cycle through the spider's images based on the animation count
        if self.is_facing_left:
            self.image = self.images_left[(self.animation_count // len(self.images_left)) % len(self.images_left)]
        else:
            self.image = self.images_right[(self.animation_count // len(self.images_right)) % len(self.images_right)]
        
        self.animation_count += 1
        # Reset the animation count after 60 frames (1 second)
        if self.animation_count == 60:
            self.animation_count = 0

    def horizontal_movement(self, dt):
        # Move the spider horizontally based on the direction it is facing
        if self.is_facing_left: 
            self.velocity.x = -1 
        else: 
            self.velocity.x = 1
        self.position.x += self.velocity.x * dt  # Update position based on velocity and time
        self.rect.x = int(self.position.x)  # Update the spider's rectangular position
        self.bottom_rect.x = int(self.position.x)  # Update the bottom rectangle for collision

    def checkCollisionsx(self, collision_tiles, empty_tiles):
        # Check for horizontal collisions with solid tiles or empty tiles (to flip direction)
        collisions = self.get_collisions(collision_tiles, self.rect)
        if self.on_ground:
            collisions = collisions + self.get_collisions(empty_tiles, self.bottom_rect)

        for tile in collisions:
            if self.velocity.x > 0 and tile.rect.x >= self.rect.x:
                if self.on_ground: 
                    self.position.x = tile.rect.left - self.rect.w  # Adjust position if colliding
                    self.rect.x = self.position.x
                    self.bottom_rect.x = self.position.x
                    self.is_facing_left = not self.is_facing_left  # Flip the direction
            elif self.velocity.x < 0 and self.is_facing_left and tile.rect.x <= self.rect.x:
                if self.on_ground: 
                    self.position.x = tile.rect.right  # Adjust position if colliding
                    self.rect.x = self.position.x
                    self.bottom_rect.x = self.position.x
                    self.is_facing_left = not self.is_facing_left  # Flip the direction

    def vertical_movement(self, dt):
        # Update vertical velocity based on gravity and time
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: 
            self.velocity.y = 7  # Limit downward speed
        self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)
        self.rect.bottom = self.position.y  # Update the spider's bounding box
        self.bottom_rect.bottom = self.position.y + TILESIZE  # Update bottom rectangle

    def checkCollisionsy(self, collision_tiles, one_way_tiles):
        # Check for vertical collisions with solid tiles and one-way tiles
        self.on_ground = False
        self.rect.bottom += 1  # Move down slightly to check for collisions
        collisions = self.get_collisions(collision_tiles, self.rect)
        for tile in collisions:
            if self.velocity.y > 0:
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top  # Adjust position on landing
                self.rect.bottom = self.position.y
                self.bottom_rect.bottom = self.position.y + TILESIZE
                self.landed_recently = True
            elif self.velocity.y < 0:
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.rect.h  # Adjust position if hitting the ceiling
                self.rect.bottom = self.position.y
                self.bottom_rect.bottom = self.position.y + TILESIZE
        # Check for one-way collisions (tiles that pass through when falling)
        one_way_collisions = self.get_collisions(one_way_tiles, self.rect)
        for tile in one_way_collisions:
            if self.velocity.y > 0:
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.rect.bottom = self.position.y
                self.bottom_rect.bottom = self.position.y + TILESIZE
                self.landed_recently = True

    def jump(self):
        # Define jump zones based on spider's position and facing direction
        jump_zone_left = self.position.x - (TILESIZE * 3) if self.is_facing_left else self.position.x + (TILESIZE * 1)
        jump_zone_right = self.position.x - (TILESIZE * 1) if self.is_facing_left else self.position.x + (TILESIZE * 3)
        jump_zone_bottom = self.position.y + (TILESIZE * 3)
        jump_zone_top = self.position.y - (TILESIZE * 3)
        
        # Check if the player is within the jump zone and if the spider is on the ground
        left_check = self.player.position.x >= jump_zone_left
        right_check = self.player.position.x <= jump_zone_right
        top_check = self.player.position.y >= jump_zone_top
        bottom_check = self.player.position.y <= jump_zone_bottom

        if not (left_check and right_check and top_check and bottom_check and self.on_ground):
            return  # Skip jumping if conditions are not met

        if random.random() < 0.05:  # 5% chance to make the spider jump
            self.is_jumping = True
            self.velocity.y -= 8  # Apply upward velocity for the jump
            self.on_ground = False

    def get_collisions(self, tiles, rect):
        # Check for collisions between the spider and tiles based on the provided rectangle
        collisions = []
        for tile in tiles:
            if tile.rect.colliderect(rect):
                collisions.append(tile)
        return collisions  # Return the list of colliding tiles

    def draw(self, surface, camera):
        surface.blit(self.image[0], (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
        surface.blit(self.image[1], (self.rect.x + TILESIZE - camera.offset.x, self.rect.y - camera.offset.y))
    
    def update(self, collision_tiles, empty_tiles, one_way_tiles, dt):
        if self.is_facing_left == True:
            self.bottom_rect = pygame.Rect((self.rect.x, self.rect.y + TILESIZE), (TILESIZE, TILESIZE))
        else:
            self.bottom_rect = pygame.Rect((self.rect.x - TILESIZE, self.rect.y + TILESIZE), (TILESIZE, TILESIZE))
        
        self.horizontal_movement(dt)
        self.checkCollisionsx(collision_tiles, empty_tiles)
        self.vertical_movement(dt)
        self.checkCollisionsy(collision_tiles, one_way_tiles)
        self.jump()
        self.animate()