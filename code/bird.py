import pygame
import random
import math
from settings import *
from utils import *
from enum import Enum

# Define the states of the bird during its behavior
class BirdState(Enum):
    PATROL = 0  # Bird is patrolling in its designated area
    DIVE = 1  # Bird is diving toward the player
    RECOVER = 2  # Bird is recovering from a dive

# Class for Bird Enemy that chases after player
class Bird:
    def __init__(self, pos, sprite_sheet, player):
        # Initialize the bird's position, velocity, gravity, and rect for collision detection
        self.position, self.velocity = pygame.math.Vector2(pos), pygame.math.Vector2(0, 0)
        self.gravity = 0.5
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.rect = pygame.Rect(self.position, (TILESIZE, TILESIZE))
        self.is_facing_left = False  # Indicates if the bird is facing left
        self.player = player  # Reference to the player object
        self.init_images(sprite_sheet)  # Initialize bird images from the sprite sheet
        self.animation_count = 0  # For cycling through animation frames
        self.state = BirdState.PATROL  # Bird starts in patrol state
        
        self.start_pos = pygame.math.Vector2(pos)  # Starting position of the bird
        self.target = pygame.math.Vector2(0, 0)  # Target position for movement
        self.max_velocity = 1.5  # Maximum speed of the bird
        self.patrol_radius = 3  # Radius within which the bird patrols

        self.animate()  # Start the bird animation

    def init_images(self, sprite_sheet):
        # Initialize the images for the bird when facing left and right
        image_1 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('bird')), SPRITE_SHEET_WIDTH)
        image_1.set_colorkey(BLACK)  # Remove the black color from the sprite (transparency)
        image_2 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('bird')) + 3, SPRITE_SHEET_WIDTH)
        image_2.set_colorkey(BLACK)
        image_3 = sprite_sheet.get_sprite_from_id(int(SS_DIC.get('bird')) + 6, SPRITE_SHEET_WIDTH)
        image_3.set_colorkey(BLACK)

        self.images_left = [image_1, image_2, image_3]  # List of images when facing left

        self.images_right = []  # List of images when facing right
        for image in self.images_left:
            image_right = pygame.transform.flip(image, True, False)  # Flip each image horizontally
            self.images_right.append(image_right)

    def animate(self):
        # Check if the bird is facing left and select the appropriate image set
        if self.is_facing_left:
            # Set the image based on the current frame count, cycling through images_left
            # Use modulo to loop back to the first image after the last one
            self.image = self.images_left[(self.animation_count // len(self.images_left)) % len(self.images_left)]
        else:
            # Set the image based on the current frame count, cycling through images_right
            # Use modulo to loop back to the first image after the last one
            self.image = self.images_right[(self.animation_count // len(self.images_right)) % len(self.images_right)]
        
        # Increment the animation count to move to the next frame
        self.animation_count += 1

        # Reset the animation count every 60 frames
        if self.animation_count == 60:
            self.animation_count = 0

    def checkCollisionsx(self, collision_tiles):
        # Get all tiles that collide with bird
        collisions = self.get_collisions(collision_tiles, self.rect)
        
        for tile in collisions:
            # If the bird is moving to the right (positive velocity in the x-direction)
            if self.velocity.x > 0 and tile.rect.x >= self.rect.x:
                # Adjust the bird's position so it doesn't overlap with the tile (move bird to the left edge of the tile)
                self.position.x = tile.rect.left - self.rect.w
                self.rect.x = self.position.x

                # Flip the bird's facing direction since it collided with a tile while moving right
                self.is_facing_left = not self.is_facing_left

                # If the bird is in the dive state, change to the recover state
                if self.state == BirdState.DIVE:
                    self.state == BirdState.RECOVER
                    # Save the bird's current position as its starting position for recovery
                    self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                    # Set the target position to a location above the bird's current position
                    self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
                    # Stop the bird's movement by setting the velocity to zero
                    self.velocity.x = 0
                    self.velocity.y = 0
                    
            # If the bird is moving to the left (negative velocity in the x-direction)
            elif self.velocity.x < 0 and self.is_facing_left and tile.rect.x <= self.rect.x:
                # Adjust the bird's position so it doesn't overlap with the tile (move bird to the right edge of the tile)
                self.position.x = tile.rect.right
                self.rect.x = self.position.x

                # Flip the bird's facing direction since it collided with a tile while moving left
                self.is_facing_left = not self.is_facing_left

                # If the bird is in the dive state, change to the recover state
                if self.state == BirdState.DIVE:
                    self.state == BirdState.RECOVER
                    # Save the bird's current position as its starting position for recovery
                    self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                    # Set the target position to a location above the bird's current position
                    self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
                    # Stop the bird's movement by setting the velocity to zero
                    self.velocity.x = 0
                    self.velocity.y = 0

    def checkCollisionsy(self, collision_tiles):
        # Get all tiles that collide with the bird
        collisions = self.get_collisions(collision_tiles, self.rect)
        
        for tile in collisions:
            # If the bird is moving down (positive velocity in the y-direction)
            if self.velocity.y > 0:
                # Stop downward movement (reset vertical velocity)
                self.velocity.y = 0

                # Adjust the bird's position so it doesn't overlap with the tile (move bird to the top edge of the tile)
                self.position.y = tile.rect.top - TILESIZE
                self.rect.bottom = self.position.y

                # Change the bird's state to RECOVER when it hits something while moving down
                self.state = BirdState.RECOVER
                # Save the bird's current position as its starting position for recovery
                self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                # Set the target position to a location above the bird's current position
                self.target = pygame.math.Vector2(self.position.x, self.position.y - (3 * TILESIZE))
                # Stop the bird's horizontal and vertical movement
                self.velocity.x = 0
                self.velocity.y = 0

            # If the bird is moving up (negative velocity in the y-direction)
            elif self.velocity.y < 0:
                # Stop upward movement (reset vertical velocity)
                self.velocity.y = 0

                # Adjust the bird's position so it doesn't overlap with the tile (move bird to the bottom edge of the tile)
                self.position.y = tile.rect.bottom + self.rect.h
                self.rect.bottom = self.position.y

                # Change the bird's state to PATROL when it hits something while moving up
                self.state = BirdState.PATROL
                # Save the bird's current position as its starting position for patrolling
                self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)
                # Stop the bird's horizontal and vertical movement
                self.velocity.x = 0
                self.velocity.y = 0

    def calculate_movement(self, dt):
        # Perform actions based on bird's state
        if self.state == BirdState.PATROL:
            self.patrol()
        elif self.state == BirdState.DIVE:
            self.dive(dt)
        elif self.state == BirdState.RECOVER:
            self.recover(dt)

    def patrol(self):
        # Set target positions based on direction the bird is facing
        if self.is_facing_left:
            # If the bird is facing left, set the target to be a certain distance to the left
            self.target.x = self.start_pos.x - self.patrol_radius * TILESIZE
        else:
            # If the bird is facing right, set the target to be a certain distance to the right
            self.target.x = self.start_pos.x + self.patrol_radius * TILESIZE

        # Check if the bird has moved past its target patrol position
        if self.position.x <= self.target.x and self.is_facing_left:
            # If the bird has reached or passed the left boundary, change direction to move right
            self.is_facing_left = False
            self.velocity.x = self.max_velocity  # Set velocity to move right
        elif self.position.x >= self.target.x and not self.is_facing_left:
            # If the bird has reached or passed the right boundary, change direction to move left
            self.is_facing_left = True
            self.velocity.x = -self.max_velocity  # Set velocity to move left
        else:
            # If within bounds of the patrol area, continue moving in the current direction
            self.velocity.x = self.max_velocity if not self.is_facing_left else -self.max_velocity

        # Define a "dive zone" where the bird might switch to DIVE state based on player proximity
        dive_zone_left = self.position.x - (TILESIZE * 3) if self.is_facing_left else self.position.x + (TILESIZE * 1)
        dive_zone_right = self.position.x - (TILESIZE * 1) if self.is_facing_left else self.position.x + (TILESIZE * 3)
        dive_zone_bottom = self.position.y + (TILESIZE * 3)
        dive_zone_top = self.position.y + (TILESIZE * 1)

        # Check if the player is within the dive zone
        left_check = self.player.position.x >= dive_zone_left
        right_check = self.player.position.x <= dive_zone_right
        bottom_check = self.player.position.y <= dive_zone_bottom
        top_check = self.player.position.y >= dive_zone_top

        # If the player is not in the dive zone, do nothing and continue patrolling
        if not (left_check and right_check and top_check and bottom_check):
            return

        # If the player is in the dive zone, with a 50% chance, switch to DIVE state
        if random.random() < 0.5:
            self.state = BirdState.DIVE
            self.velocity.x = 0  # Stop horizontal movement
            self.velocity.y = 0  # Stop vertical movement
            self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)  # Set new start position
            self.target = pygame.math.Vector2(self.player.position.x, self.player.position.y)  # Set player position as new target

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
        self.velocity.x = direction_x * self.max_velocity * 2
        self.velocity.y = direction_y * self.max_velocity * 2

        # Check if bird has reached the target (or is very close)
        if distance < TILESIZE:  # Tolerance to stop the bird when it's near the target
            self.target = pygame.math.Vector2(self.position, self.position.y - (3 * TILESIZE))
            self.state = BirdState.RECOVER  # Switch to recovery state

    def recover(self, dt):
        # Set the bird's vertical velocity to move upwards
        self.velocity.y = -self.max_velocity

        # Check if the bird has reached or passed the target position
        if self.rect.y <= self.target.y:
            # If the bird reaches the recovery target, switch back to PATROL state
            self.state = BirdState.PATROL

            # Update the bird's starting position to its current position after recovery
            self.start_pos = pygame.math.Vector2(self.position.x, self.position.y)

            # Stop the bird's horizontal and vertical velocity as it returns to patrolling
            self.velocity.x = 0
            self.velocity.y = 0

    def horizontal_movement(self, dt):
        # Update the bird's horizontal position based on its velocity and the elapsed time (dt)
        self.position.x += self.velocity.x * dt

        # Update the bird's rectangle position to reflect the new horizontal position
        self.rect.x = self.position.x

    def vertical_movement(self, dt):
        # Update the bird's vertical position based on its velocity and the elapsed time (dt)
        self.position.y += self.velocity.y * dt

        # Update the bird's rectangle position to reflect the new vertical position
        self.rect.y = self.position.y

    def get_collisions(self, tiles, rect):
        collisions = []

        # Check for collisions with all the provided tiles
        for tile in tiles:
            if tile.rect.colliderect(rect):
                # If a collision is detected, add the tile to the collisions list
                collisions.append(tile)

        # Return the list of tiles that are colliding with the provided rectangle (rect)
        return collisions

    def draw(self, surface, camera):
        # Draw the bird's image onto the given surface, adjusting for the camera's offset
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))

    def update(self, collision_tiles, dt):
        # Update the bird's movement based on its current state and elapsed time
        self.calculate_movement(dt)

        # Update horizontal movement and handle horizontal collisions
        self.horizontal_movement(dt)
        self.checkCollisionsx(collision_tiles)

        # Update vertical movement and handle vertical collisions
        self.vertical_movement(dt)
        self.checkCollisionsy(collision_tiles)

        # Animate the bird's sprite
        self.animate()