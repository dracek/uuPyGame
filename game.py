import threading
from datetime import datetime

import uuid
import pygame
import socketio

from inputs import InputManager, PLAYER_KEYMAPS
from player import Player
from npc import NPC

from config import GAME_FPS, CLIENT_REFRESH_COEF


class AbstractGame:
    """Abstract ancestor"""

    def __init__(self, **kwargs):
        self.input_manager = InputManager()

        self.screen = kwargs["screen"]
        self.clock = pygame.time.Clock()
        self.running = True
        self.tick = GAME_FPS
        self.players = {}
        self.npcs = []                    # todo DICT by id????

    def short_uid(self, length=8):
        return uuid.uuid4().hex[:length]

    def handle_events(self):
        """Handles events and interruptions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Pressed quitting!")
                self.running = False

    def handle_key_events(self):
        """Handles key presses"""
        raise NotImplemented


    def update_players(self,  **kwargs):
        """Handles players updates"""

        for player in self.players.values():
            player.update(inputs = self.input_manager.get_inputs(player.uid), **kwargs)
            self.input_manager.clear_inputs(player.uid)


    def update_npcs(self,  **kwargs):
        """Handles npcs updates"""

        for npc in self.npcs:
            npc.update(players = self.players, **kwargs)


    def render_all(self):
        """Draws itself"""
        self.screen.fill((0, 0, 0))

        for player in self.players.values():
            player.draw(self.screen)

        for npc in self.npcs:
            npc.draw(self.screen)


    def run(self):
        """Running loop"""
        while self.running:
            self.handle_events()
            self.handle_key_events()

            self.update_players()
            self.update_npcs()

            self.render_all()
            pygame.display.flip()
            self.clock.tick(self.tick)

        print("Closing game ....")




class SingleGame(AbstractGame):
    """Single player game"""

    PLAYER1 = "Player1"
    PLAYER2 = "Player2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pl1 = Player(self.PLAYER1)       # todo some better init
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
        self.sio = socketio.Client()
        self.sio.on('message', self.message)
        self.sio.on('info', self.info)

        self.sio.on('move', self.move)


    def run(self):
        """Running loop"""

        # sio běží v neblokujícím vlákně
        self.client_thread = threading.Thread(target=self.start_client, daemon=True)
        self.client_thread.start()

        cnt = 0 # todo implement better info heartbeat

        while self.running:

            if not self.sio.connected:
                print("Connecting to server")  # todo better gui!
            else:
                self.handle_events()
                self.handle_key_events()

                self.update_players()
                self.update_npcs()
                self.send_all_positions()

                self.render_all()
                pygame.display.flip()

                cnt += 1
                if cnt > 200:
                    print("heartbeat!")
                    now = datetime.now()
                    print(now.strftime("%H:%M:%S.%f")[:-3])
                    self.sio.emit("info")
                    cnt = 0

            self.clock.tick(self.tick)

        print("Closing game!")
        self.sio.disconnect()
        self.client_thread.join()


    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)

    def start_client(self):
        # todo nejak posílat player color
        # todo config ?

        headers = {"role": "host", "uid": self.PLAYER1, "name": self.PLAYER1_NAME }
        self.sio.connect("http://localhost:3333", headers=headers, transports=["websocket"])
        # self.sio.connect("https://drsnyjelen.cz/", headers=headers, transports=["websocket"])

        self.sio.wait()

    def send_all_positions(self):
        player_data = [player.get_transport_data() for player in self.players.values()]

        npc_data = [] # todo :)

        self.sio.emit("game_state", {"players": player_data, "npcs": npc_data})


    def message(self, msg):
        print("Got new message!", msg)

    def info(self, msg):
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
        print(data, "Got move!", data)
        self.input_manager.add_inputs(data.uid, data.inputs)


class MultiGameClient(AbstractGame):
    """Multi-player game, role client"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.PLAYER1 = self.short_uid()
        self.PLAYER1_NAME = "Some player" # todo config?
        pl1 = Player(self.PLAYER1)
        pl1.set_coords(20,20)
        pl1.set_name(self.PLAYER1_NAME)
        self.players[self.PLAYER1] = pl1

        self.input_manager.add_keymap(self.PLAYER1, PLAYER_KEYMAPS["wasd"])

        self.npcs.append(NPC(400, 400))

        self.client_thread = None
        self.sio = socketio.Client()
        self.sio.on('message', self.message)
        self.sio.on('info', self.info)

        self.sio.on('game_state', self.game_state)


    def run(self):
        """Running loop"""

        # sio běží v neblokujícím vlákně
        self.client_thread = threading.Thread(target=self.start_client, daemon=True)
        self.client_thread.start()

        cnt = 0

        while self.running:

            if not self.sio.connected:
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                print("Connecting to server") # todo some nice screen, add some waiting for host
            else:
                self.handle_events()
                self.handle_key_events()
                self.send_key_events()

                # no drawing, only from game_state event!

                cnt += 1
                if cnt > (200 * CLIENT_REFRESH_COEF):
                    print("heartbeat!")
                    now = datetime.now()
                    print(now.strftime("%H:%M:%S.%f")[:-3])
                    self.sio.emit("info")
                    cnt = 0

            self.clock.tick(self.tick * CLIENT_REFRESH_COEF) # rychlejsi tick, protoze se updatuje eventem

        print("Closing game!")
        self.sio.disconnect()
        self.client_thread.join()


    def handle_key_events(self):
        """Handles key presses"""

        keys = pygame.key.get_pressed()

        for key in PLAYER_KEYMAPS["wasd"].keys():
            if keys[key]:
                self.input_manager.add_input(self.PLAYER1, key)

    def send_key_events(self):
        """Send key presses to socket"""

        inputs = self.input_manager.get_inputs(self.PLAYER1)
        self.input_manager.clear_inputs(self.PLAYER1)
        if len(inputs) > 0:
            self.sio.emit("move", {"uid": self.PLAYER1, "inputs": inputs})

    def start_client(self):
        # todo posílat color v hexa
        # todo adress config ?

        headers = {"role": "client", "uid": self.PLAYER1, "name": self.PLAYER1_NAME }
        self.sio.connect("http://localhost:3333", headers=headers, transports=["websocket"])
        # self.sio.connect("https://drsnyjelen.cz/", headers=headers, transports=["websocket"])

        self.sio.wait()

    def message(self, msg):
        print("Got new message!", msg)

    def info(self, msg):
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
        print(data, "Got new game state!", data)

        for player_data in data.players:
            if player_data.uid in self.players:
                pl = self.players.get(player_data.uid)
                pl.update_data(player_data)

        # self.update_npcs()

        self.render_all()
        pygame.display.flip()



