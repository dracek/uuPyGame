import pygame
import math

from pygame.examples.scrap_clipboard import screen

BULLET_SPEED = 5
BULLET_SIZE = 5

class Bullet:
    def __init__(self, x, y, target_x, target_y,color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED
        self.color = color

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen):
        pygame.draw.rect(screen,self.color, self.rect)

    def is_off_screen(self):
        return (self.rect.x < 0 or self.rect.x > 800 or
                self.rect.y < 0 or self.rect.y > 600)