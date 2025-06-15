"""Main module"""

import sys
import os
sys.path.append(os.path.dirname(__file__))  # ✅ Ensures local imports work

import pygame

from enums import GameType
from game import SingleGame, CoopGame
from ui import show_menu, show_splash, show_end_message
from config import SCREEN_WIDTH, SCREEN_HEIGHT  # ✅ Use screen resolution from config

def main():
    """Main function of this game"""

    pygame.init()

    # Set up window using fixed resolution from config.py
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moje Střilečka")

    # Load and scale background to match config resolution
    bg_path = os.path.join("assets", "sprites", "background", "heli.png")
    raw_bg = pygame.image.load(bg_path).convert()
    background = pygame.transform.scale(raw_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    show_splash(screen)

    while True:
        choice = show_menu(screen)

        if choice == GameType.SINGLE:
            game = SingleGame(screen=screen, background=background)
            result = game.run()
            if result == "win":
                show_end_message(screen, f"You win! Score: {game.score}")
            elif result == "lost":
                show_end_message(screen, f"You lost. Score: {game.score}")

        elif choice == GameType.COOP:
            game = CoopGame(screen=screen, background=background)
            result = game.run()
            if result == "win":
                show_end_message(screen, f"You win! Score: {game.score}")
            elif result == "lost":
                show_end_message(screen, f"You lost. Score: {game.score}")
            else:
                show_end_message(screen, "Game ended.")

        elif choice == "quit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()