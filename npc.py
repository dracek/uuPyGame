"""NPC module"""
import math

import pygame

from config import NPC_SPEED
from bullet import Bullet


class NPC:
    """NPC common class"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def update(self, **kwargs):
        """Updates self position according to players"""
        nearest_player = self.find_closest_player(self, kwargs["players"].values())


        if self.rect.x < nearest_player.rect.x:
            self.rect.x += NPC_SPEED
        elif self.rect.x > nearest_player.rect.x:
            self.rect.x -= NPC_SPEED
        if self.rect.y < nearest_player.rect.y:
            self.rect.y += NPC_SPEED
        elif self.rect.y > nearest_player.rect.y:
            self.rect.y -= NPC_SPEED

    def get_shot_target(self, players):
        return self.find_closest_player(self, players)

   # def shoot(self, target):
   #     bullet = Bullet(self.rect.centerx, self.rect.centery,
   #                     target.rect.centerx, target.rect.centery,
   #                     color=(255, 0, 0))
   #     self.bullets.append(bullet)

    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


    def distance(self, rect1, rect2):
        """Helper function for distance computing"""
        return math.hypot(rect1.x - rect2.x, rect1.y - rect2.y)

    def find_closest_player(self, npc, players):
        """Function for NPC to find which player to chase, not optimized"""
        closest = None
        min_dist = float('inf')

        for player in players:
            dist = self.distance(npc.rect, player.rect)
            if dist < min_dist:
                min_dist = dist
                closest = player

        return closest
