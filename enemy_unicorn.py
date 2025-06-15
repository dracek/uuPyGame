import os
import pygame
from enemy import Enemy
from spritesheet import SpriteSheet

class UnicornEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        # Custom stats
        self.health = 60
        self.max_health = 60
        self.damage = 8
        self.speed = 1.5
        self.score = 15
        self.frame_delay = 120

        # Sprite settings
        self.sprite_cols = 5  # actions
        self.sprite_rows = 4  # directions
        self.sprite_scale = 0.3
        self.frame_width = 32
        self.frame_height = 32
        self.rect = pygame.Rect(x, y, int(self.frame_width * self.sprite_scale), int(self.frame_height * self.sprite_scale))

        # Load animations
        self.animations = self.load_animations()

        # Animation state
        self.animation_state = {
            "direction": "down",
            "action": "idle",
            "frame_index": 0,
            "last_update": pygame.time.get_ticks()
        }

        self.animate()  # Ensure self.image is initialized

    def load_animations(self):
        animations = {}
        direction_order = ["down", "left", "right", "up"]
        action_order = ["idle", "idle2", "move", "move2", "shoot"]

        sprite_path = os.path.join("assets", "sprites", "characters", "Unicorn.png")
        sheet = SpriteSheet(sprite_path)
        grid = sheet.load_grid(cols=self.sprite_cols, rows=self.sprite_rows, scale=self.sprite_scale)

        for row, direction in enumerate(direction_order):
            for col, action in enumerate(action_order):
                key = (direction, action)
                try:
                    animations[key] = [grid[row][col]]  # ✅ grab the correct frame
                except IndexError:
                    print(f"[WARN] Missing frame at row {row}, col {col} for key {key}")
                    animations[key] = []

        return animations


    def update(self, **kwargs):
        players = kwargs["players"]
        living_players = [p for p in players.values() if p.health > 0]
        if not living_players:
            return

        target = self.find_closest(living_players)
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery

        direction = self.get_direction(dx, dy)
        self.animation_state["direction"] = direction

        if abs(dx) > 2 or abs(dy) > 2:
            self.rect.x += self.speed if dx > 0 else -self.speed
            self.rect.y += self.speed if dy > 0 else -self.speed
            self.animation_state["action"] = "move"
        else:
            self.animation_state["action"] = "idle"

        self.animate()

    def animate(self):
        now = pygame.time.get_ticks()
        state = self.animation_state
        key = (state["direction"], state["action"])

        if key not in self.animations:
            print(f"[WARN] Missing animation for {key}, defaulting to ('down', 'idle')")
            key = ("down", "idle")

        frames = self.animations[key]
        if now - state["last_update"] > self.frame_delay:
            state["frame_index"] = (state["frame_index"] + 1) % len(frames)
            state["last_update"] = now

        self.image = frames[state["frame_index"]]

    def draw(self, screen):
        if not isinstance(self.image, pygame.Surface):
            print("[ERROR] self.image is not a Surface:", type(self.image))
            return
        screen.blit(self.image, self.rect.topleft)
        self.draw_lifebar(screen)
