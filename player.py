import pygame
from settings import *

class Player():
    def __init__(self, sprite_sheet, display, initial_pos, level):
        self.left_key, self.right_key, self.facing_left = False, False, False
        self.is_jumping, self.on_ground = False, True
        self.gravity, self.friction = .35, -.12
        self.position, self.velocity = pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.display = display
        self.position = pygame.math.Vector2(initial_pos)
        
        self.init_images(sprite_sheet)
        self.animation_state = 'IDLE_RIGHT'
        self.animation_count = 0
        self.animate()
        
        self.rect = self.image.get_rect(topleft = self.position)
        
        self.is_active = True
        self.death_timer = 0

        self.level = level
        
    def init_images(self, sprite_sheet):
        idle_images_right = []
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

        idle_images_left = []
        for image in idle_images_right:
            idle_image_left = pygame.transform.flip(image, True, False)
            idle_image_left.set_colorkey(BLACK)
            idle_images_left.append(idle_image_left)

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

        running_images_left = []
        for image in running_images_right:
            running_image_left = pygame.transform.flip(image, True, False)
            running_image_left.set_colorkey(BLACK)
            running_images_left.append(running_image_left)

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
        
        death_image_right = pygame.transform.rotate(sprite_sheet.get_sprite_from_id(13, 192), 180)
        death_image_right.set_colorkey(BLACK)
        death_image_left = pygame.transform.flip(death_image_right, True, False)
        death_image_left.set_colorkey(BLACK)

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

    def update_animation_state(self):
        if abs(self.velocity.x) < 0.1:
            self.animation_state = 'IDLE'
        elif abs(self.velocity.x) > 0.1:
            self.animation_state = 'RUN'

        if not self.on_ground and self.velocity.y < 0:
            self.animation_state = 'JUMP'
        elif not self.on_ground and self.velocity.y >= 0:
            self.animation_state = 'FALL'
        
        if self.facing_left:
            self.animation_state = self.animation_state + '_LEFT'
        else:
            self.animation_state = self.animation_state + '_RIGHT'

    def animate(self):
        images = self.image_dict[self.animation_state]
        self.image = images[(self.animation_count // len(images)) % len(images)]
        self.animation_count += 1
        if self.animation_count == 60:
            self.animation_count = 0
    
    def draw(self, camera):
        self.display.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y)) 
        #self.display.blit(self.image, (self.rect.x, self.rect.y)) 

    def update(self, dt, collision_tiles, damage_tiles, one_way_tiles, player_data):
        if self.is_active:
            self.horizontal_movement(dt)
            self.checkCollisionsx(collision_tiles, damage_tiles)
            self.vertical_movement(dt)
            self.checkCollisionsy(collision_tiles, one_way_tiles, damage_tiles)
            self.update_animation_state()
            self.animate()
        else:
            self.die(dt, player_data)

    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.left_key:
            self.acceleration.x -= .3
        elif self.right_key:
            self.acceleration.x += .3
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(4)
        self.position.x += self.velocity.x * dt + (self.acceleration.x * .5) * (dt * dt)
        self.rect.x = int(self.position.x)

    def checkCollisionsx(self, collision_tiles, damage_tiles):
        collisions = self.get_collisions(collision_tiles)
        for tile in collisions:
            if self.velocity.x > 0:
                self.position.x = tile.rect.left - self.rect.w
                self.rect.x = self.position.x
            elif self.velocity.x < 0:
                self.position.x = tile.rect.right
                self.rect.x = self.position.x
        damages = self.get_collisions(damage_tiles)
        for tile in damages:
            self.init_death()
        
    def checkCollisionsy(self, collision_tiles, one_way_tiles, damage_tiles):
        self.on_ground = False
        self.rect.bottom += 1
        collisions = self.get_collisions(collision_tiles)
        for tile in collisions:
            if self.velocity.y > 0:
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.rect.bottom = self.position.y
            elif self.velocity.y < 0:
                self.velocity.y = 0
                self.position.y = tile.rect.bottom + self.rect.h
                self.rect.bottom = self.position.y
        one_way_collisions = self.get_collisions(one_way_tiles)
        for tile in one_way_collisions:
            if self.velocity.y > 0:
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.position.y = tile.rect.top
                self.rect.bottom = self.position.y
        damages = self.get_collisions(damage_tiles)
        for tile in damages:
            self.init_death()

    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: self.velocity.y = 7
        self.position.y += self.velocity.y * dt + (self.acceleration.y * .5) * (dt * dt)
        self.rect.bottom = self.position.y

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.velocity.y -= 8
            self.on_ground = False

    def limit_velocity(self, max_vel):
        if self.velocity.x > max_vel:
            self.velocity.x = max_vel
        elif self.velocity.x < -max_vel:
            self.velocity.x = -max_vel
        
        if abs(self.velocity.x) < 0.01:
            self.velocity.x = 0

    def get_collisions(self, tiles):
        collisions = []
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                collisions.append(tile)
        return collisions
    
    def init_death(self):
        self.is_active = False
    
    def die(self, dt, player_data):
        if self.facing_left:
            self.image = self.image_dict['DEATH_LEFT']
        else:
           self.image = self.image_dict['DEATH_RIGHT']
        self.death_timer += 1
        self.vertical_movement(dt)
        if self.death_timer == 180:
            player_data.lives -= 1
            self.level.reset = True
