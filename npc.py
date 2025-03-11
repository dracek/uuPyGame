"""NPC module"""
import pygame

class NPC:
    """NPC common class"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def update(self, player):
        """Updates self position according to player"""
        if self.rect.x < player.rect.x:
            self.rect.x += 2
        elif self.rect.x > player.rect.x:
            self.rect.x -= 2
        if self.rect.y < player.rect.y:
            self.rect.y += 2
        elif self.rect.y > player.rect.y:
            self.rect.y -= 2

    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
