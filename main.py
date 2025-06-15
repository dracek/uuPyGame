"""Main module"""

import pygame

from enums import GameType
from game import SingleGame, CoopGame
from ui import show_menu, show_splash
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
            game.run()

        if choice == GameType.COOP:
            game = CoopGame(screen=screen)
            game.run()

        elif choice == "quit":
            break


    pygame.quit()

if __name__ == "__main__":
    main()
