"""Game module"""


import pygame
import random


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
        self.score = 0
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_interval_range = (3000, 5000)

        self.game_result = None


    def spawn_random_npc(self):
        npc_type = random.choices(
            ["easy", "medium", "hard"],
            weights=[70, 25, 5],
            k=1
        )[0]
        x = random.randint(50, self.screen.get_width() - 50)
        y = random.randint(50, self.screen.get_height() - 50)
        self.npcs.append(NPC(x, y, npc_type=npc_type))


    def try_spawn_npc(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time > self.next_spawn_interval:
            self.spawn_random_npc()
            self.last_spawn_time = now
            # Nastav nový random interval pro další spawn
            self.next_spawn_interval = random.randint(*self.spawn_interval_range)

    def try_npc_shoot(self, npc):
        now = pygame.time.get_ticks()
        npc_id = id(npc)

        if now - self.npc_last_shot_times.get(npc_id, 0) < self.npc_shoot_cooldown:
            return

        target = npc.get_shot_target(
            [p for p in self.players.values() if p.health > 0]
        )

        if not target:
            return

        bullet = Bullet(
            npc.rect.centerx, npc.rect.centery,
            target.rect.centerx, target.rect.centery,
            color=(255, 0, 0),
            shooter=npc
        )
        self.npc_bullets.append(bullet)
        self.npc_last_shot_times[npc_id] = now


    def check_bullet_collisions(self):
        # NPC střely na hráče
        for bullet in self.npc_bullets[:]:
            for npc in self.npcs:
                if bullet.shooter == npc:
                    for player in self.players.values():
                        if bullet.rect.colliderect(player.rect):
                            player.health -= npc.damage
                            self.npc_bullets.remove(bullet)
                            break
                    break


        for bullet in self.player_bullets[:]:
            for npc in self.npcs[:]:
                if bullet.rect.colliderect(npc.rect):
                    npc.health -= 10
                    if npc.health <= 0:
                        self.npcs.remove(npc)
                        self.score += npc.score
                    self.player_bullets.remove(bullet)
                    break


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
            if player.health <= 0:
                continue

            inputs = self.input_manager.get_inputs(player.uid)
            player.update(inputs = inputs, **kwargs)


            if KeyType.SHOOT.name in inputs:
                bullet = player.shoot(self.npcs)
                if bullet is not None:
                    self.player_bullets.append(bullet)


            self.input_manager.clear_inputs(player.uid)

    def update_npcs(self, **kwargs):
        """Handles npcs updates"""

        for npc in self.npcs[:]:
            npc.update(players=self.players, **kwargs)
            self.try_npc_shoot(npc)

            for player in self.players.values():
                if player.health <= 0:
                    continue

                if npc.rect.colliderect(player.rect):
                    player.health -= npc.damage * 2
                    self.npcs.remove(npc)
                    break




    def render_all(self):
        """Draws itself"""
        self.screen.fill((0, 0, 0))

        for player in self.players.values():
            if player.health > 0:
                player.draw(self.screen)


        for npc in self.npcs:
            npc.draw(self.screen)


        for bullet in self.player_bullets:
            bullet.draw(self.screen)


        for bullet in self.npc_bullets:
            bullet.draw(self.screen)


        font = pygame.font.SysFont(None, 30)
        score_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 10))


    def update_bullets(self):
        """Update bullets position"""
        for bullet_list in [self.player_bullets, self.npc_bullets]:
            for bullet in bullet_list[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullet_list.remove(bullet)

    def check_game_end(self):
        alive_players = [p for p in self.players.values() if p.health > 0]
        if not alive_players:
            if self.score >= 200:
                self.game_result = "win"
            else:
                self.game_result = "lost"
            self.running = False

    def run(self):
        """Running loop"""
        self.next_spawn_interval = random.randint(*self.spawn_interval_range)
        while self.running:
            self.handle_events()
            self.handle_key_events()


            self.try_spawn_npc()


            self.update_players()
            self.update_npcs()
            self.update_bullets()


            self.render_all()
            pygame.display.flip()
            self.clock.tick(self.tick)
            self.check_bullet_collisions()
            self.check_game_end()


        print("Closing game ....")
        return self.game_result




class SingleGame(AbstractGame):
    """Single player game"""


    PLAYER1 = "Player1"


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        pl1 = Player(self.PLAYER1)       # todo some better init
        pl1.set_coords(20,20)
        self.players[self.PLAYER1] = pl1


        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])


        self.spawn_random_npc()


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

