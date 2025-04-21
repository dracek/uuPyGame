"""Main module"""

import pygame

from enums import GameType
from game import SingleGame, MultiGameHost, MultiGameClient
from ui import show_menu
from config import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()

def main():
    """Main function of this game"""

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Moje Střilečka")

    while True:
        choice = show_menu(screen)

        print("Choice", choice)

        if choice == GameType.SINGLE:
            game = SingleGame(screen=screen)
            game.run()

        if choice == GameType.HOST:
            game = MultiGameHost(screen=screen)
            game.run()

        if choice == GameType.CLIENT:
            game = MultiGameClient(screen=screen)
            game.run()

        elif choice == "quit":
            break


    pygame.quit()

if __name__ == "__main__":
    main()
