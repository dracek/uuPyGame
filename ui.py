"""UI module"""

import pygame
from decorators import log_decorator
from enums import GameType


@log_decorator
def show_menu(screen):
    """Main game menu"""
    font = pygame.font.Font(None, 36)
    menu_options = ["1: Single player",
                    "2: Cooperative",
                    "ESC: Ukončení"]

    while True:
        screen.fill((0, 0, 128))
        for i, option in enumerate(menu_options):
            text = font.render(option, True, (255, 255, 255))
            screen.blit(text, (50, 200 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:

                print("Key pressed:", event.key)

                if event.key == 49: #pygame.K_1:
                    return GameType.SINGLE
                if event.key == 50: #pygame.K_2:
                    return GameType.COOP

                if event.key == pygame.K_ESCAPE:
                    return "quit"
