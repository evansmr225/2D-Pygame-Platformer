import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        self.image = image
        self.position = pygame.math.Vector2(x, y)
        self.rect = self.image.get_rect(topleft=(x,y))

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))
        #surface.blit(self.image, (self.rect.x, self.rect.y)) 