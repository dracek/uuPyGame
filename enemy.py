"""Enemy base module"""
import math
import pygame
from config import NPC_SPEED

class Enemy:
    """Base enemy class, extendable for specific enemy types like Unicorn"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.speed = NPC_SPEED
        self.score = 25
        self.rect = pygame.Rect(x, y, 32, 32)  # Default size; override in subclass
        self.animations = {}
        self.direction = "down"
        self.action = "idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 100  # ms
        self.image = None

    def update(self, **kwargs):
        """Updates position and animation"""
        players = [p for p in kwargs["players"].values() if p.health > 0]
        if not players:
            return

        nearest = self.find_closest(players)

        dx = dy = 0
        if nearest.rect.x > self.rect.x:
            dx = self.speed
            self.direction = "right"
        elif nearest.rect.x < self.rect.x:
            dx = -self.speed
            self.direction = "left"

        if nearest.rect.y > self.rect.y:
            dy = self.speed
            self.direction = "down"
        elif nearest.rect.y < self.rect.y:
            dy = -self.speed
            self.direction = "up"

        if dx != 0 or dy != 0:
            self.action = "move"
        else:
            self.action = "idle"

        self.rect.x += dx
        self.rect.y += dy

        self.animate()

    def animate(self):
        """Updates animation frames"""
        key = (self.direction, self.action)
        if key not in self.animations:
            return

        now = pygame.time.get_ticks()
        if now - self.frame_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.animations[key])
            self.image = self.animations[key][self.frame_index]
            self.frame_timer = now

    def get_direction(self, dx, dy):
        """Returns cardinal direction string based on movement delta"""
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
        

    def get_shot_target(self, players):
        """Select target player"""
        players = [p for p in players if p.health > 0]
        return self.find_closest(players) if players else None

    def draw_lifebar(self, screen):
        bar_width = self.rect.width
        fill = (self.health / self.max_health) * bar_width
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 10, fill, 5))
    
    def draw(self, screen):
        """Draws enemy with visible border"""
        if self.image:
            # Create a rect centered on current position, based on image size
            image_rect = self.image.get_rect(center=self.rect.center)
            
            # Draw the image
            screen.blit(self.image, image_rect)

        else:
            # If no image, draw fallback red rectangle + border
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
            pygame.draw.rect(screen, (0, 0, 255), self.rect, 1)

        self.draw_lifebar(screen)


    def distance(self, rect1, rect2):
        return math.hypot(rect1.centerx - rect2.centerx, rect1.centery - rect2.centery)

    def find_closest(self, players):
        closest = min(players, key=lambda p: self.distance(self.rect, p.rect))
        return closest
