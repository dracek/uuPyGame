"""Game module"""

import queue
import threading
import time
from datetime import datetime


import uuid

import psutil
import pygame
import socketio

from bullet import Bullet
from inputs import InputManager, PLAYER_KEYMAPS
from player import Player
from npc import NPC

from config import GAME_FPS, CLIENT_REFRESH_COEF, INFO_TIMER, GATEWAY_ADDRESS


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
        self.last_shot_times = {}
        self.shoot_cooldown = 250
        self.npc_last_shot_times = {}
        self.npc_shoot_cooldown = 150

    def try_shoot(self, uid, target_pos):
        now = pygame.time.get_ticks()
        last_shot = self.last_shot_times.get(uid, 0)
        if now - last_shot >= self.shoot_cooldown:
            player = self.players[uid]
            bullet = player.shoot(target_pos, color=player.color)
            self.player_bullets.append(bullet)
            self.last_shot_times[uid] = now

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



    def short_uid(self, length=8):
        """Helper uid function"""
        return uuid.uuid4().hex[:length]

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
            player.update(inputs = self.input_manager.get_inputs(player.uid), **kwargs)
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
    #PLAYER2 = "Player2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pl1 = Player(self.PLAYER1)       # todo some better init
        pl1.set_coords(20,20)
        self.players[self.PLAYER1] = pl1

        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])

        #pl2 = Player(self.PLAYER2)  # experimental player 2
        #pl2.set_coords(100, 20)
        #pl2.color = (0,0,255)
        #self.players[self.PLAYER2] = pl2

        #self.input_manager.add_keymap(self.PLAYER2, PLAYER_KEYMAPS["arrows"])

        self.npcs.append(NPC(400, 400))

    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)

        #for key in PLAYER_KEYMAPS["arrows"].keys():
            #if keys[key]:
                #self.input_manager.add_input(self.PLAYER2, key)

        if mouse_buttons[0]:
            self.try_shoot(self.PLAYER1, pygame.mouse.get_pos())


class MultiGameHost(AbstractGame):
    """Multi-player game, role host"""

    PLAYER1 = "HOST" # todo some short id
    PLAYER1_NAME = "Libor" # todo config?

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pl1 = Player(self.PLAYER1)
        pl1.set_coords(20,20)
        pl1.set_name(self.PLAYER1_NAME)
        self.players[self.PLAYER1] = pl1

        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])

        self.npcs.append(NPC(400, 400))

        self.client_thread = None
        self.info_thread = None
        self.socket_thread = None
        self.socket_queue = queue.Queue()

        self.sio = socketio.Client()
        self.sio.on('message', self.message)
        self.sio.on('info', self.info)

        self.sio.on('move', self.move)

    def run(self):
        """Running loop"""

        # sio běží v neblokujícím vlákně
        self.client_thread = threading.Thread(target=self.start_client, daemon=True)
        self.client_thread.start()

        self.info_thread = threading.Thread(target=self.start_info, daemon=True)
        self.info_thread.start()

        self.socket_thread = threading.Thread(target=self.start_socket, daemon=True)
        self.socket_thread.start()

        while self.running:

            if not self.sio.connected:
                print("Connecting to server")  # todo better gui!
            else:
                self.handle_events()
                self.handle_key_events()

                self.update_players()
                self.update_npcs()
                self.update_bullets()
                self.send_all_positions()

                self.render_all()
                pygame.display.flip()

            self.clock.tick(self.tick)

        print("Closing game!")
        self.info_thread.join()
        self.socket_thread.join()
        self.sio.disconnect()
        self.client_thread.join()




    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)

        if mouse_buttons[0]:
            self.try_shoot(self.PLAYER1, pygame.mouse.get_pos())


    def start_socket(self):
        """ Vlákno pro komunikaci přes socket, které bude odebírat data z fronty """
        while self.running:
            try:
                while not self.socket_queue.empty():  # Zpracuj všechny dostupné zprávy
                    name, data = self.socket_queue.get_nowait()
                    # print("emitted", name )
                    self.sio.emit(name, data)

            except queue.Empty:
                pass  # Pokud fronta je prázdná, čekáme

            time.sleep(0.01)

    def start_info(self):
        """Info heartbeat thread"""
        while self.running:
            time.sleep(INFO_TIMER)  # Pauza 1 sekunda
            if self.sio.connected:
                print("heartbeat!")
                now = datetime.now()
                print(now.strftime("%H:%M:%S.%f")[:-3])
                self.sio.emit("info")

    def start_client(self):
        """SIO connection thread"""
        headers = {"role": "host", "uid": self.PLAYER1, "name": self.PLAYER1_NAME }
        self.sio.connect(GATEWAY_ADDRESS, headers=headers, transports=["websocket"])
        self.sio.wait()

    def send_all_positions(self):
        """Position synchronizing method"""

        player_data = [player.get_transport_data() for player in self.players.values()]

        npc_data = [] # todo :)

        self.socket_queue.put(("game_state", {"players": player_data, "npcs": npc_data}))


    def message(self, msg):
        """Message handler"""
        print("Got new message!", msg)

    def info(self, msg):
        """Info handler"""
        now = datetime.now()
        print(now.strftime("%H:%M:%S.%f")[:-3])
        print("Got info!", msg)

        for client in msg.get("clientList", []):    # add missing players
            uid = client["uid"]
            if uid not in self.players:

                print("New player", client.get("name"))
                new_player = Player(uid)
                new_player.set_coords(20, 20)
                new_player.set_name(client.get("name"))
                self.players[uid] = new_player

    def move(self, data):
        """Incoming move handler"""
        # print(data, "Got move!", data)
        self.input_manager.add_inputs(data["uid"], data["inputs"])


class MultiGameClient(AbstractGame):
    """Multi-player game, role client"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player1_id = self.short_uid()
        self.player1_name = "Some player" # todo config?
        pl1 = Player(self.player1_id)
        pl1.set_coords(20,20)
        pl1.set_name(self.player1_name)
        self.players[self.player1_id] = pl1

        self.input_manager.add_keymap(self.player1_id, PLAYER_KEYMAPS["wasd"])

        self.npcs.append(NPC(400, 400))

        self.client_thread = None
        self.socket_thread = None
        self.socket_queue = queue.Queue()

        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=20,
            reconnection_delay=0.1,
            reconnection_delay_max=5
        )

        # sio handlers
        self.sio.on('message', self.message)
        self.sio.on('info', self.info)
        self.sio.on('game_state', self.game_state)

        # sio info block
        self.sio.on("connect", lambda: print("connected"))
        self.sio.on("disconnect", lambda x: print("disconnected", x))
        self.sio.on("reconnect", lambda x: print("reconnected", x))
        self.sio.on("reconnect_error", lambda x: print("reconnect-error", x))


    def run(self):
        """Running loop"""

        # sio běží v neblokujícím vlákně
        self.client_thread = threading.Thread(target=self.start_client, daemon=True)
        self.client_thread.start()

        self.socket_thread = threading.Thread(target=self.start_socket, daemon=True)
        self.socket_thread.start()

        cnt = 0

        while self.running:

            if not self.sio.connected:
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                print("Connecting to server") # todo some nice screen, add some waiting for host
            else:
                self.handle_events()
                self.handle_key_events()
                self.update_bullets()
                self.send_key_events()

                # no drawing, only from game_state event!

                cnt += 1
                if cnt > (200 * CLIENT_REFRESH_COEF):
                    cpu = psutil.cpu_percent()
                    print(f"CPU: {cpu}")
                    print("heartbeat!")
                    now = datetime.now()
                    print(now.strftime("%H:%M:%S.%f")[:-3])
                    self.sio.emit("info")
                    cnt = 0

            # todo: rychlejsi tick, protoze se updatuje eventem
            # ale pozor na zahlceni socketu
            self.clock.tick(self.tick * CLIENT_REFRESH_COEF)

        print("Closing game!")
        self.sio.disconnect()
        self.client_thread.join()

    def start_socket(self):
        """ Vlákno pro komunikaci přes socket, které bude odebírat data z fronty """
        while self.running:
            try:
                while not self.socket_queue.empty():  # Zpracuj všechny dostupné zprávy
                    name, data = self.socket_queue.get_nowait()
                    # print("emitted", name )
                    if self.sio.connected:
                        self.sio.emit(name, data)

            except queue.Empty:
                pass  # Pokud fronta je prázdná, čekáme

            time.sleep(0.02)

    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.player1_id, key)

        if mouse_buttons[0]:
            self.try_shoot(self.PLAYER1, pygame.mouse.get_pos())

    def send_key_events(self):
        """Send key presses to socket"""

        inputs = self.input_manager.get_inputs(self.player1_id)
        self.input_manager.clear_inputs(self.player1_id)
        if len(inputs) > 0:
#            self.sio.emit("move", {"uid": self.PLAYER1, "inputs": inputs})
            self.socket_queue.put(("move", {"uid": self.player1_id, "inputs": inputs}))

    def start_client(self):
        """Sio connect thread"""

        # todo posílat color v hexa

        headers = {"role": "client", "uid": self.player1_id, "name": self.player1_name}
        self.sio.connect(GATEWAY_ADDRESS, wait_timeout=5, headers=headers, transports=["websocket"])

        self.sio.wait()

    def message(self, msg):
        """Message handler"""
        print("Got new message!", msg)

    def info(self, msg):
        """Info handler"""
        now = datetime.now()
        print(now.strftime("%H:%M:%S.%f")[:-3])
        print("Got info!", msg)

        for client in msg.get("clientList", []):    # add missing players
            uid = client["uid"]
            if uid not in self.players:

                print("New player", client.get("name"))
                new_player = Player(uid)
                new_player.set_coords(20, 20)
                new_player.set_name(client.get("name"))
                self.players[uid] = new_player

    def game_state(self, data):
        """Incoming game state handler"""
        # print(data, "Got new game state!", data)

        for player_data in data["players"]:
            if player_data["uid"] in self.players:
                pl = self.players.get(player_data["uid"])
                pl.update_data(player_data)
        # self.update_npcs()

        self.render_all()

        pygame.display.flip()
