import pygame
from spritesheet import SpriteSheet
import os

class Assets:
    def __init__(self):
        self.player_frames = {}
        self.load_player_frames()

        self.unicorn_bullet = self.load_unicorn_bullet()  # ✅ Preload unicorn bullet

    def load_player_frames(self):
        sprite_path = os.path.join("assets", "sprites", "characters", "Player.png")
        sheet = SpriteSheet(sprite_path)

        cols, rows = 5, 4  # actions × directions
        grid = sheet.load_grid(cols=cols, rows=rows, scale=0.4)

        directions = ["down", "left", "right", "up"]
        actions = ["walk1", "walk2", "walk3", "shoot1", "shoot2"]

        self.player_frames = {}
        for row_idx, direction in enumerate(directions):
            for col_idx, action in enumerate(actions):
                frame = grid[row_idx][col_idx]
                key = (direction, action)
                self.player_frames[key] = [frame]

    def load_unicorn_bullet(self):
        path = os.path.join("assets", "sprites", "bullets", "unicorn_bullet.png")
        try:
            image = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(image, (32, 32))
            print("[DEBUG] Unicorn bullet loaded:", scaled.get_size())
            return scaled
        except Exception as e:
            print(f"[ERROR] Could not load unicorn bullet: {e}")
            return None

