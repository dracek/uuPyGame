"""Main module"""

import pygame

from enums import GameType
from game import SingleGame, CoopGame
from ui import show_menu, show_splash, show_end_message
from config import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()

def main():
    """Main function of this game"""

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moje Střilečka")

    show_splash(screen)

    while True:
        choice = show_menu(screen)

        #print("Choice", choice)

        if choice == GameType.SINGLE:
            game = SingleGame(screen=screen)
            result = game.run()
            if result == "win":
                show_end_message(screen, f"You win! Score: {game.score}")
            elif result == "lost":
                show_end_message(screen, f"You lost.Score: {game.score}")

        if choice == GameType.COOP:
            game = CoopGame(screen=screen)
            result = game.run()
            if result == "win":
                show_end_message(screen, f"You win!Score: {game.score}")
            elif result == "lost":
                show_end_message(screen, f"You lost.Score: {game.score}")
            else:
                show_end_message(screen, "Game ended.")

        elif choice == "quit":
            break


    pygame.quit()

if __name__ == "__main__":
    main()
