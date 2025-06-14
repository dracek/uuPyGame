"""Game module"""

import pygame

from bullet import Bullet
from enums import KeyType
from inputs import InputManager, PLAYER_KEYMAPS
from player import Player
from npc import NPC

from config import GAME_FPS


class AbstractGame:
    """Abstract game ancestor"""

    def __init__(self, **kwargs):
        self.input_manager = InputManager()

        self.screen = kwargs["screen"]
        self.clock = pygame.time.Clock()
        self.running = True
        self.tick = 1 * GAME_FPS
        self.players = {}
        self.npcs = []                    # todo DICT by id????

        self.bullets = []
        self.player_bullets = []
        self.npc_bullets = []

        self.npc_last_shot_times = {}
        self.npc_shoot_cooldown = 500


    def try_npc_shoot(self, npc):
        now = pygame.time.get_ticks()
        npc_id = id(npc)
        last_shot = self.npc_last_shot_times.get(npc_id, 0)
        if now - last_shot >= self.npc_shoot_cooldown:
            target = npc.get_shot_target(self.players.values())
            if target:
                bullet = Bullet(npc.rect.centerx, npc.rect.centery,
                                target.rect.centerx, target.rect.centery,
                                color=(255, 0, 0))
                self.npc_bullets.append(bullet)
                self.npc_last_shot_times[npc_id] = now

    def handle_events(self):
        """Handles events and interruptions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Pressed quitting!")
                self.running = False

    def handle_key_events(self):
        """Handles key presses"""
        raise NotImplementedError


    def update_players(self,  **kwargs):
        """Handles players updates"""

        for player in self.players.values():

            inputs = self.input_manager.get_inputs(player.uid)

            player.update(inputs = inputs, **kwargs)

            if KeyType.SHOOT.name in inputs:
                bullet = player.shoot(self.npcs)
                if bullet is not None:
                    self.player_bullets.append(bullet)

            self.input_manager.clear_inputs(player.uid)


    def update_npcs(self,  **kwargs):
        """Handles npcs updates"""

        for npc in self.npcs:
            npc.update(players = self.players, **kwargs)
            self.try_npc_shoot(npc)


    def render_all(self):
        """Draws itself"""
        self.screen.fill((0, 0, 0))

        for player in self.players.values():
            player.draw(self.screen)

        for npc in self.npcs:
            npc.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        for bullet in self.npc_bullets:
            bullet.draw(self.screen)

    def update_bullets(self):
        """Update bullets position"""
        for bullet_list in [self.player_bullets, self.npc_bullets]:
            for bullet in bullet_list[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullet_list.remove(bullet)


    def run(self):
        """Running loop"""
        while self.running:
            self.handle_events()
            self.handle_key_events()

            self.update_players()
            self.update_npcs()
            self.update_bullets()

            self.render_all()
            pygame.display.flip()
            self.clock.tick(self.tick)

        print("Closing game ....")


class SingleGame(AbstractGame):
    """Single player game"""

    PLAYER1 = "Player1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pl1 = Player(self.PLAYER1)       # todo some better init
        pl1.set_coords(20,20)
        self.players[self.PLAYER1] = pl1

        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])

        self.npcs.append(NPC(400, 400))

    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)


class CoopGame(AbstractGame):
    """Single player game"""

    PLAYER1 = "Player1"
    PLAYER2 = "Player2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pl1 = Player(self.PLAYER1)
        pl1.set_coords(20,20)
        self.players[self.PLAYER1] = pl1

        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])

        pl2 = Player(self.PLAYER2)  # experimental player 2
        pl2.set_coords(100, 20)
        pl2.color = (0,0,255)
        self.players[self.PLAYER2] = pl2

        self.input_manager.add_keymap(self.PLAYER2, PLAYER_KEYMAPS["arrows"])

        self.npcs.append(NPC(400, 400))


    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)

        for key in PLAYER_KEYMAPS["arrows"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER2, key)
