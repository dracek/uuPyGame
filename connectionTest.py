"""Socket-testing standalone module"""

import socketio

from config import GATEWAY_ADDRESS

sio = socketio.Client()

sio.on("connect", lambda: print("connected"))
sio.on("disconnect", lambda x: print("disconnected", x))
sio.on("reconnect", lambda x: print("reconnected", x))
sio.on("reconnect_error", lambda x: print("re-er", x))

print("connecting...")
sio.connect(GATEWAY_ADDRESS)
sio.wait()
