"""Player module"""
import math
import pygame


from config import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT
from enums import KeyType, Facing
from bullet import Bullet


movement_keys = {KeyType.LEFT.name, KeyType.RIGHT.name, KeyType.UP.name, KeyType.DOWN.name}


class Player:
    """Player class init"""
    def __init__(self, uid):


        self.uid = uid
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = (0, 255, 0)
        self.name = "Player1"
        self.speed = PLAYER_SPEED
        self.is_moving = False
        self.facing = Facing.RIGHT
        self.health = 100
        self.max_health = 100




        self.shoot_cooldown = 250
        self.last_shot_time = pygame.time.get_ticks()




    def set_coords(self, x, y):
        """Coords setter"""
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)


    def set_name(self, name):
        """Name setter"""
        self.name = name


    def update(self, **kwargs):
        """Update self position from move intention"""


        inp = kwargs["inputs"]


        self.is_moving = any(key in inp for key in movement_keys)


        if KeyType.UP.name in inp:
            self.rect.y -= self.speed
            self.facing = Facing.UP
        elif KeyType.DOWN.name in inp:
            self.rect.y += self.speed
            self.facing = Facing.DOWN


        if KeyType.LEFT.name in inp:
            self.rect.x -= self.speed
            self.facing = Facing.LEFT
        elif KeyType.RIGHT.name in inp:
            self.rect.x += self.speed
            self.facing = Facing.RIGHT


        # overflow corrections - todo možná udělat přes kolize s okrajem!
        self.rect.x = max(self.rect.x, 0)
        self.rect.y = max(self.rect.y, 0)
        self.rect.x = min(self.rect.x, SCREEN_WIDTH - PLAYER_WIDTH)
        self.rect.y = min(self.rect.y, SCREEN_HEIGHT - PLAYER_HEIGHT)


    def distance(self, rect1, rect2):
        """Helper function for distance computing"""
        return math.hypot(rect1.centerx - rect2.centerx, rect1.centery - rect2.centery)


    def find_closest_npc(self, npcs):
        closest = None
        min_dist = float('inf')


        for npc in npcs:
            dist = self.distance(self.rect, npc.rect)
            if dist < min_dist:
                min_dist = dist
                closest = npc


        return closest




    def shoot(self, npcs):
        """Try to shoot, does not fire in cooldown"""


        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            target = self.find_closest_npc(npcs)
            if target is None:
                return None


            target_pos = (target.rect.centerx, target.rect.centery)
            bullet = Bullet(self.rect.centerx, self.rect.centery, *target_pos, color=self.color)
            self.last_shot_time = now
            return bullet


    def draw_lifebar(self, screen):
        bar_width = self.rect.width
        bar_heigth = 5
        fill = (self.health / self.max_health) * bar_width


        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_heigth))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 10, fill, bar_heigth))


    def draw(self, screen):
        """Draws itself"""
        pygame.draw.rect(screen, self.color, self.rect)
        self.draw_lifebar(screen)

