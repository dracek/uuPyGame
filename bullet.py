import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BULLET_SIZE, BULLET_SPEED




class Bullet:
   def __init__(self, x, y, target_x, target_y,color=(0, 0, 0),shooter=None):
       self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
       angle = math.atan2(target_y - y, target_x - x)
       self.dx = math.cos(angle) * BULLET_SPEED
       self.dy = math.sin(angle) * BULLET_SPEED
       self.color = color
       self.shooter = shooter


   def update(self):
       self.rect.x += self.dx
       self.rect.y += self.dy


   def draw(self, screen):
       pygame.draw.rect(screen,self.color, self.rect)


   def is_off_screen(self):
       return (self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or
               self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT)

