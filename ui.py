"""UI module"""
import os

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
        screen.fill((43, 28, 88))
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

def show_splash(screen):
    """Init splash screen"""

    bg_path = os.path.join("assets", "sprites", "background", "intro.png")
    background = pygame.image.load(bg_path).convert()
    background = pygame.transform.scale(background, screen.get_size())

    screen.blit(background, (0, 0))
    pygame.display.flip()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def show_end_message(screen, message):
    font = pygame.font.SysFont(None, 60)
    text = font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.fill((0, 0, 0))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(3000)
