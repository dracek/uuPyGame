"""NPC module"""
import math

import pygame

from config import NPC_SPEED
from bullet import Bullet


class NPC:
    """NPC common class"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.bullets = []
        self.shoot_cooldown = 60
        self.shoot_timer = 0

    def update(self, **kwargs):
        """Updates self position according to players"""
        players = kwargs["players"].values()
        nearest_player = self.find_closest_player(self, kwargs["players"].values())


        if self.rect.x < nearest_player.rect.x:
            self.rect.x += NPC_SPEED
        elif self.rect.x > nearest_player.rect.x:
            self.rect.x -= NPC_SPEED
        if self.rect.y < nearest_player.rect.y:
            self.rect.y += NPC_SPEED
        elif self.rect.y > nearest_player.rect.y:
            self.rect.y -= NPC_SPEED

        if self.shoot_timer <= 0:
            self.shoot(nearest_player)
            self.shoot_timer = self.shoot_cooldown
        else:
            self.shoot_timer -= 1

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]

    def shoot(self, target):
        bullet = Bullet(self.rect.centerx, self.rect.centery,
                        target.rect.centerx, target.rect.centery,
                        color=(255, 0, 0))
        self.bullets.append(bullet)

    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)


    def distance(self, rect1, rect2):
        return math.hypot(rect1.x - rect2.x, rect1.y - rect2.y)

    def find_closest_player(self, npc, players):
        closest = None
        min_dist = float('inf')

        for player in players:
            dist = self.distance(npc.rect, player.rect)
            if dist < min_dist:
                min_dist = dist
                closest = player

        return closest
