import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image
        
    def load_grid(self, cols, rows, scale=1.0):
        grid = []
        frame_width = self.sheet.get_width() // cols
        frame_height = self.sheet.get_height() // rows

        for row in range(rows):
            row_frames = []
            for col in range(cols):
                frame = self.get_image(
                    col * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height
                )
                if scale != 1.0:
                    frame = pygame.transform.scale(
                        frame,
                        (int(frame_width * scale), int(frame_height * scale))
                    )
                row_frames.append(frame)
            grid.append(row_frames)

        return grid  # 2D grid[row][col]
