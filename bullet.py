import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BULLET_SIZE, BULLET_SPEED

class Bullet:
    def __init__(self, x, y, target_x, target_y, color=(0, 0, 0), shooter=None, image=None):
        self.shooter = shooter
        self.color = color
        self.original_image = image  # Original, unrotated image
        self.image = None
        self.image_rect = None

        # Calculate movement vector
        angle = math.atan2(target_y - y, target_x - x)
        self.angle_deg = math.degrees(angle)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED

        # Positioning
        self.rect = pygame.Rect(0, 0, BULLET_SIZE, BULLET_SIZE)
        self.rect.center = (x, y)

        # ✅ Apply rotation if image provided
        if self.original_image:
            try:
                rotated = pygame.transform.rotate(self.original_image, -self.angle_deg + 180)
                self.image = rotated
                self.image_rect = self.image.get_rect(center=self.rect.center)
                print("[Bullet] Rotated image created successfully")
            except Exception as e:
                print("[Bullet ERROR] Rotation failed:", e)
                self.image = None
                self.image_rect = None
        else:
            print("[Bullet] No image provided, using color:", self.color)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.image_rect:
            self.image_rect.center = self.rect.center

    def draw(self, screen):
        if self.image and self.image_rect:
            screen.blit(self.image, self.image_rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def is_off_screen(self):
        return (
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT
        )
