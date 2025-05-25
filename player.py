"""Player module"""

import pygame
from config import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from enums import KeyType
from bullet import Bullet
import random

class Player:
    """Player class init"""
    def __init__(self, uid):

        self.uid = uid
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = (0, 255, 0)
        self.name = "Player1"
        self.speed = PLAYER_SPEED


    def set_coords(self, x, y):
        """Coords setter"""
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def set_name(self, name):
        """Name setter"""
        self.name = name


    def get_transport_data(self):
        """Prepare data for data event"""
        return {"uid": self.uid, "x": self.rect.x, "y": self.rect.y}

    def update_data(self, transport_data):
        """Update self position from data event"""
        self.rect.x = transport_data["x"]
        self.rect.y = transport_data["y"]

    def update(self, **kwargs):
        """Update self position from move intention"""

        inp = kwargs["inputs"]
        mouse_pos = kwargs.get("mouse_pos",(self.rect.centerx,self.rect.centery))

        if KeyType.LEFT.name in inp:
            self.rect.x -= self.speed
        if KeyType.RIGHT.name in inp:
            self.rect.x += self.speed
        if KeyType.UP.name in inp:
            self.rect.y -= self.speed
        if KeyType.DOWN.name in inp:
            self.rect.y += self.speed

        # overflow corrections
        self.rect.x = max(self.rect.x, 0)
        self.rect.y = max(self.rect.y, 0)
        self.rect.x = min(self.rect.x, SCREEN_WIDTH - PLAYER_WIDTH)
        self.rect.y = min(self.rect.y, SCREEN_HEIGHT - PLAYER_HEIGHT)



    def shoot(self, target_pos=None, color=None):
        if target_pos is None:
            target_pos = (400, 300)

        if color is None:
            color = self.color

        bullet = Bullet(self.rect.centerx, self.rect.centery, *target_pos, color=color)
        return bullet

    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, self.color, self.rect)
