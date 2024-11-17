import pygame
from settings import *
from falling_platform import *
from enum import Enum

# Enum to manage the player's state (normal, dying, or ending level)
class PlayerState(Enum):
    NORMAL = 0
    DYING = 1
    ENDING = 2

# Player object class
class Player():
    def __init__(self, sprite_sheet, display, initial_pos, level):
        # Initialize movement variables
        self.left_key, self.right_key, self.facing_left = False, False, False
        self.is_jumping, self.on_ground = False, True
        self.gravity, self.friction = .35, -.12
        self.position, self.velocity = pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)  # Gravity applied to acceleration
        self.display = display
        self.position = pygame.math.Vector2(initial_pos)  # Set initial position
        
        # Load and set up sprite images from sprite sheet
        self.init_images(sprite_sheet)
        self.animation_state = 'IDLE_RIGHT'  # Default animation state
        self.animation_count = 0  # Animation counter for cycling frames
        self.animate()
        
        self.rect = self.image.get_rect(topleft=self.position)  # Set the player's rectangle for collision

        # Initialize player state variables
        self.is_active = True
        self.state = PlayerState.NORMAL  # Start in normal state
        self.death_timer = 0  # Timer for death animation

        # Sound effects
        self.bonk_sound = pygame.mixer.Sound('./sounds/bonk-46000.mp3')
        self.jump_sound = pygame.mixer.Sound('./sounds/cartoon-jump-6462.mp3')
        self.death_sound = pygame.mixer.Sound('./sounds/drop-sound-effect-240899.mp3')
        self.victory_sound = pygame.mixer.Sound('./sounds/congratulations-deep-voice-172193.mp3')

        # Reference to level object
        self.level = level
    
    # Initialize the player's images for different actions (idle, running, jumping, etc.)
    def init_images(self, sprite_sheet):
        idle_images_right = []
        
        # set idle images for animation
        idle_image = sprite_sheet.get_sprite_from_id(13, 192)
        idle_image.set_colorkey(BLACK)
        idle_images_right.append(idle_image)
        idle_image = sprite_sheet.get_sprite_from_id(16, 192)
        idle_image.set_colorkey(BLACK)
        idle_images_right.append(idle_image)
        idle_image = sprite_sheet.get_sprite_from_id(19, 192)
        idle_image.set_colorkey(BLACK)
        idle_images_right.append(idle_image)
        idle_image = sprite_sheet.get_sprite_from_id(22, 192)
        idle_image.set_colorkey(BLACK)
        idle_images_right.append(idle_image)

        # flip idle images for left side
        idle_images_left = []
        for image in idle_images_right:
            idle_image_left = pygame.transform.flip(image, True, False)
            idle_image_left.set_colorkey(BLACK)
            idle_images_left.append(idle_image_left)

        # set running images for animation
        running_images_right = []
        running_image = sprite_sheet.get_sprite_from_id(49, 192)
        running_image.set_colorkey(BLACK)
        running_images_right.append(running_image)
        running_image = sprite_sheet.get_sprite_from_id(52, 192)
        running_image.set_colorkey(BLACK)
        running_images_right.append(running_image)
        running_image = sprite_sheet.get_sprite_from_id(55, 192)
        running_image.set_colorkey(BLACK)
        running_images_right.append(running_image)
        running_image = sprite_sheet.get_sprite_from_id(58, 192)
        running_image.set_colorkey(BLACK)
        running_images_right.append(running_image)

        # flip running images for left side
        running_images_left = []
        for image in running_images_right:
            running_image_left = pygame.transform.flip(image, True, False)
            running_image_left.set_colorkey(BLACK)
            running_images_left.append(running_image_left)

        # set jumping and falling images for right and left
        jumping_image_right = sprite_sheet.get_sprite_from_id(85, 192)
        jumping_image_right.set_colorkey(BLACK)
        jumping_image_left = pygame.transform.flip(jumping_image_right, True, False)
        jumping_image_left.set_colorkey(BLACK)
        falling_image_right = sprite_sheet.get_sprite_from_id(88, 192)
        falling_image_right.set_colorkey(BLACK)
        falling_image_left = pygame.transform.flip(falling_image_right, True, False)
        falling_image_left.set_colorkey(BLACK)
        jumping_image_right = [jumping_image_right]
        jumping_image_left = [jumping_image_left]
        falling_image_right = [falling_image_right]
        falling_image_left = [falling_image_left]

        # set death image for right and left
        death_image_right = pygame.transform.rotate(sprite_sheet.get_sprite_from_id(13, 192), 180)
        death_image_right.set_colorkey(BLACK)
        death_image_left = pygame.transform.flip(death_image_right, True, False)
        death_image_left.set_colorkey(BLACK)

        # add all images to dictionary which will be iterated through for animating
        self.image_dict = {
            'IDLE_RIGHT': idle_images_right,
            'IDLE_LEFT': idle_images_left,
            'RUN_RIGHT': running_images_right,
            'RUN_LEFT': running_images_left,
            'JUMP_RIGHT': jumping_image_right,
            'JUMP_LEFT': jumping_image_left,
            'FALL_RIGHT': falling_image_right,
            'FALL_LEFT': falling_image_left,
            'DEATH_RIGHT': death_image_right,
            'DEATH_LEFT': death_image_left
        }   

    # Update the player's animation state based on their movement and position
    def update_animation_state(self):
        if abs(self.velocity.x) < 0.1:
            self.animation_state = 'IDLE'  # Idle state when no horizontal movement
        elif abs(self.velocity.x) > 0.1:
            self.animation_state = 'RUN'  # Running state when moving horizontally

        # Jump or fall states based on vertical velocity and ground status
        if not self.on_ground and self.velocity.y < 0:
            self.animation_state = 'JUMP'
        elif not self.on_ground and self.velocity.y >= 0:
            self.animation_state = 'FALL'
        
        # Flip animation state based on facing direction (left or right)
        if self.facing_left:
            self.animation_state += '_LEFT'
        else:
            self.animation_state += '_RIGHT'

    # Animate the player by cycling through frames based on the current animation state
    def animate(self):
        images = self.image_dict[self.animation_state]  # Get images for the current animation state
        self.image = images[(self.animation_count // len(images)) % len(images)]  # Cycle through frames
        self.animation_count += 1
        if self.animation_count == 60: # Reset counter after 60
            self.animation_count = 0  
    
    # Draw the player on the screen at their current position, considering camera offset
    def draw(self, camera):
        self.display.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y)) 

    # Handles movement, collision checks, and state updates
    def update(self, dt, collision_tiles, damage_tiles, one_way_tiles, end_goal, player_data):
        if self.state == PlayerState.NORMAL:
            self.horizontal_movement(dt)
            self.checkCollisionsx(collision_tiles, damage_tiles, end_goal)
            self.vertical_movement(dt)
            self.checkCollisionsy(collision_tiles, one_way_tiles, damage_tiles, end_goal)
            self.update_animation_state()
            self.animate()
        elif self.state == PlayerState.DYING:
            self.die(dt, player_data)
        elif self.state == PlayerState.ENDING:
            self.end_level()

    def horizontal_movement(self, dt):
        # Reset horizontal acceleration to 0 before applying any new forces
        self.acceleration.x = 0

        # If the left key is pressed, apply a force to move the player left
        if self.left_key:
            self.acceleration.x -= .3
        # If the right key is pressed, apply a force to move the player right
        elif self.right_key:
            self.acceleration.x += .3

        # Apply friction to the current velocity to gradually slow down the player
        self.acceleration.x += self.velocity.x * self.friction

        # Update the velocity based on the acceleration and the time delta (dt)
        self.velocity.x += self.acceleration.x * dt

        # Limit the maximum speed to avoid the player moving too fast
        self.limit_velocity(4)

        # Update the player's position based on the velocity and the acceleration (to simulate smooth movement)
        self.position.x += self.velocity.x * dt + (self.acceleration.x * .5) * (dt * dt)

        # Update the player's rectangle position based on the new position
        self.rect.x = int(self.position.x)

    def checkCollisionsx(self, collision_tiles, damage_tiles, end_goal):
        # Get all tiles that the player may be colliding with horizontally
        collisions = self.get_collisions(collision_tiles)
        for tile in collisions:
            # If moving right (positive velocity), check for collisions with the left side of the tile
            if self.velocity.x > 0:
                self.position.x = tile.rect.left - self.rect.w  # Move the player to the left edge of the tile
                self.rect.x = self.position.x
            # If moving left (negative velocity), check for collisions with the right side of the tile
            elif self.velocity.x < 0:
                self.position.x = tile.rect.right  # Move the player to the right edge of the tile
                self.rect.x = self.position.x

        # Check for collisions with damage tiles (e.g., spikes, traps)
        damages = self.get_collisions(damage_tiles)
        for tile in damages:
            self.state = PlayerState.DYING  # If hit, set player state to "DYING"

        # Check if the player has reached the end goal (level exit)
        if end_goal.rect.colliderect(self.rect):
            self.state = PlayerState.ENDING  # Set player state to "ENDING" when goal is reached
        
    def checkCollisionsy(self, collision_tiles, one_way_tiles, damage_tiles, end_goal):
        # Check if the player is on the ground by setting this flag to False initially
        self.on_ground = False
        self.rect.bottom += 1  # Slightly move the player down to check for collisions

        # Get all tiles the player may be colliding with vertically
        collisions = self.get_collisions(collision_tiles)
        for tile in collisions:
            # If moving down (positive velocity), check for collision with the top side of the tile
            if self.velocity.y > 0:
                self.on_ground = True  # Player is grounded
                self.is_jumping = False  # The player is no longer jumping
                self.velocity.y = 0  # Stop downward velocity (the player is now on the ground)
                self.position.y = tile.rect.top  # Position the player at the top of the tile
                self.rect.bottom = self.position.y  # Update the player's bounding box position
                if hasattr(tile, 'player_collision_event'):  # Trigger a custom event if present
                    tile.player_collision_event()
            # If moving up (negative velocity), check for collision with the bottom side of the tile
            elif self.velocity.y < 0:
                self.velocity.y = 0  # Stop upward velocity (the player has hit the bottom of a ceiling)
                self.position.y = tile.rect.bottom + self.rect.h  # Place player just below the tile
                self.rect.bottom = self.position.y  # Update the player's bounding box
                self.bonk_sound.play()  # Play sound for hitting the ceiling

        # Check for one-way collisions (the player can move through these from below but not from above)
        one_way_collisions = self.get_collisions(one_way_tiles)
        for tile in one_way_collisions:
            if self.velocity.y > 0:  # Only apply to downward movement
                self.on_ground = True  # Player is grounded
                self.is_jumping = False  # The player is no longer jumping
                self.velocity.y = 0  # Stop downward velocity
                self.position.y = tile.rect.top  # Position the player at the top of the one-way tile
                self.rect.bottom = self.position.y  # Update the player's bounding box position

        # Check for collisions with damage tiles (e.g., spikes, traps)
        damages = self.get_collisions(damage_tiles)
        for tile in damages:
            self.state = PlayerState.DYING  # If the player collides with damage tiles, set state to "DYING"
            pygame.mixer.music.stop()  # Stop the background music
            self.death_sound.play()  # Play the death sound effect

        # Check if the player has reached the end goal (level exit)
        if end_goal.rect.colliderect(self.rect):
            self.state = PlayerState.ENDING  # Set player state to "ENDING" when the goal is reached
            pygame.mixer.music.stop()  # Stop the background music
            self.victory_sound.play()  # Play the victory sound effect
        
    def vertical_movement(self, dt):
        # Update the vertical velocity based on acceleration and time delta (dt)
        self.velocity.y += self.acceleration.y * dt
        # Limit the maximum downward velocity to prevent falling too fast
        if self.velocity.y > 7: 
            self.velocity.y = 7
        # Update the player's vertical position based on velocity and acceleration
        self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)
        self.rect.bottom = self.position.y

        # Check if the player falls below a certain point (out of bounds) and set the player to the dying state
        if self.position.y >= INTERNAL_DISPLAY_HEIGHT * 2 + TILESIZE * 2 and self.state != PlayerState.DYING:
            pygame.mixer.music.stop()  # Stop the background music
            self.death_sound.play()  # Play the death sound
            self.state = PlayerState.DYING  # Change the player state to "DYING"

    def jump(self):
        # Allow the player to jump only if they are on the ground
        if self.on_ground:
            self.is_jumping = True  # Set jumping state to true
            self.velocity.y -= 8  # Apply an upward velocity to simulate jumping
            self.on_ground = False  # Player is no longer on the ground
            self.jump_sound.play()  # Play the jump sound effect

    def limit_velocity(self, max_vel):
        # Limit the player's horizontal velocity to the maximum allowed value
        if self.velocity.x > max_vel:
            self.velocity.x = max_vel
        elif self.velocity.x < -max_vel:
            self.velocity.x = -max_vel

        # If the velocity is very small (near zero), set it to exactly zero
        if abs(self.velocity.x) < 0.01:
            self.velocity.x = 0

    def get_collisions(self, tiles):
        # Initialize an empty list to store tiles that collide with the player
        collisions = []
        # Loop through all tiles and check if they intersect with the player's bounding box
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                collisions.append(tile)  # If a collision occurs, add the tile to the collisions list
        return collisions  # Return the list of collided tiles

    def die(self, dt, player_data):
        # Set the player's image to the death animation based on the direction they are facing
        if self.facing_left:
            self.image = self.image_dict['DEATH_LEFT']
        else:
            self.image = self.image_dict['DEATH_RIGHT']
        
        # Increment the death timer to track how long the player has been "dead"
        self.death_timer += 1
        # Handle vertical movement while the player is dead (e.g., falling downwards)
        self.vertical_movement(dt)
        
        # If the death timer reaches a specific time, decrement the player's lives and reset the level
        if self.death_timer == 180:
            player_data.lives -= 1  # Decrease the player's life count
            self.level.reset = True  # Set the level to reset

    def end_level(self):
        # Increment the timer to track the level completion process
        self.death_timer += 1
        
        # If the timer reaches a certain value (e.g., 180), mark the level as completed
        if self.death_timer == 180:
            self.level.completed = True  # Set the level to "completed" state
