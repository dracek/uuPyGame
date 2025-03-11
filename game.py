"""Game module"""

import pygame
from player import Player
from npc import NPC

class Game:
    """Game class"""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(400, 500)
        self.npcs = [NPC(100, 100), NPC(600, 200)]
        self.bullets = []

    def run(self):
        """Running loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        """Handles events and interruptions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Handles all entity updates"""
        self.player.update()
        for npc in self.npcs:
            npc.update(self.player)

    def render(self):
        """Draws itself"""
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)
        for npc in self.npcs:
            npc.draw(self.screen)
        pygame.display.flip()
