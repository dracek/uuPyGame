import pygame
from spritesheet import SpriteSheet

class Assets:
    def __init__(self):
        self.player_frames = []
        self.load_player_frames()

    def load_player_frames(self):
        sprite_path = "assets/sprites/characters/Player.png"
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
                self.player_frames[key] = [frame]  # one frame per action
