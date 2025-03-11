"""Main module"""

import pygame
from game import Game
from ui import show_menu

pygame.init()

def main():
    """Main function of this game"""
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Moje Střilečka")

    while True:
        choice = show_menu(screen)
        if choice == "start":
            game = Game(screen)
            game.run()
        elif choice == "quit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()
