"""Player module using directional sprite animations"""
import math
import pygame

from config import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED
from enums import KeyType, Facing
from bullet import Bullet

movement_keys = {KeyType.LEFT.name, KeyType.RIGHT.name, KeyType.UP.name, KeyType.DOWN.name}


class Player:
    def __init__(self, uid, assets, pos=(0, 0)):
        self.uid = uid
        self.assets = assets
        self.frames = self.assets.player_frames  # Dict: (direction, action) -> [Surface]
        self.image = None
        self.rect = pygame.Rect(pos[0], pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

        self.name = uid
        self.speed = PLAYER_SPEED
        self.is_moving = False
        self.facing = Facing.DOWN
        self.health = 100
        self.max_health = 100
        self.color = (0, 255, 0)

        self.shoot_cooldown = 250
        self.damage = 10  # damage dealt per shot
        self.last_shot_time = pygame.time.get_ticks()

        self.frame_timer = 0
        self.frame_index = 0
        self.frame_delay = 150  # ms
        self.current_action = "walk1"

        self.shoot_anim_time = 300  # ms to show shoot frame
        self.last_shoot_anim = 0
        self.shooting = False  # Tracks if we are currently animating a shot

    def set_coords(self, x, y):
        self.rect.topleft = (x, y)

    def set_name(self, name):
        self.name = name

    def update(self, **kwargs):
        inp = kwargs["inputs"]
        screen = kwargs.get("screen")

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

        if screen:
            sw, sh = screen.get_width(), screen.get_height()
            self.rect.x = max(0, min(self.rect.x, sw - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, sh - self.rect.height))

        self.animate()

    def animate(self):
        now = pygame.time.get_ticks()
        direction = self.facing.name.lower()

        if self.shooting:
            if now - self.last_shoot_anim > self.shoot_anim_time:
                self.shooting = False
            else:
                frame = "shoot1" if (now // 150) % 2 == 0 else "shoot2"
                key = (direction, frame)
                self.image = self.frames.get(key, self.frames.get(("down", "walk1"), [None]))[0]
                if self.image:
                    center = self.rect.center
                    self.rect = self.image.get_rect(center=center)
                return

        if self.is_moving:
            walk_cycle = ["walk1", "walk2", "walk3"]
            index = (now // self.frame_delay) % len(walk_cycle)
            action = walk_cycle[index]
        else:
            action = "walk1"

        key = (direction, action)
        self.image = self.frames.get(key, self.frames.get(("down", "walk1"), [None]))[0]

        if self.image:
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)

    def distance(self, rect1, rect2):
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
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            target = self.find_closest_npc(npcs)
            if target is None:
                return None
            target_pos = (target.rect.centerx, target.rect.centery - 8)
            bullet = Bullet(self.rect.centerx, self.rect.centery, *target_pos, color=self.color)

            self.last_shot_time = now
            self.shooting = True
            self.last_shoot_anim = now

            return bullet

    def draw_lifebar(self, screen):
        bar_width = self.rect.width
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        offset = 5
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x + offset, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x + offset, self.rect.y - 10, fill, bar_height))

        font = pygame.font.SysFont(None, 24)
        name_surface = font.render(self.name, True, self.color)
        name_rect = name_surface.get_rect(center=(self.rect.centerx + offset, self.rect.top - 20))
        screen.blit(name_surface, name_rect)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        self.draw_lifebar(screen)