"""Player module"""
import pygame

class Player:
    """Player class"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def update(self):
        """Update self position from keypressed events"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_UP]:
            self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            self.rect.y += 5

    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
