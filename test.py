from flask import Flask
from flask_socketio import SocketIO

import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    print("Starting simple server...")
    socketio.run(app, host='0.0.0.0', port=5000)
