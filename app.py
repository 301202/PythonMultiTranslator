from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
from dotenv import load_dotenv
import os
import random
from string import ascii_uppercase, digits
from googletrans import Translator
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["FLASK_DEBUG"] = os.environ.get("FLASK_DEBUG")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
translator = Translator()

rooms = {}

def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            break
    return code

def generate_unique_id(length=8):
    return ''.join(random.choice(ascii_uppercase + digits) for _ in range(length))

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        language = request.form.get("language")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name!", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code!", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": [], "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        session["language"] = language
        session["user_id"] = generate_unique_id()
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    if room not in rooms:
        return

    sender_name = session.get("name")
    original_message = data["data"]

    for member in rooms[room]["members"]:
        user_language = member["language"]
        translated_message = translator.translate(original_message, src='auto', dest=user_language).text

        content = {
            "name": sender_name,
            "message": translated_message
        }

        emit("message", content, room=member["sid"])
        print(f"Sent to {member['name']} ({user_language}): {translated_message}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    language = session.get("language")
    user_id = session.get("user_id")
    sid = request.sid
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    rooms[room]["members"].append({"name": name, "language": language, "sid": sid, "user_id": user_id})

    for member in rooms[room]["members"]:
        user_language = member["language"]
        connect_message = translator.translate("has entered the room", src='auto', dest=user_language).text
        emit("message", {"name": name, "message": connect_message}, room=member["sid"])

    print(f"{name} joined room {room} with language {language}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    language = session.get("language")
    user_id = session.get("user_id")
    sid = request.sid
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] = [member for member in rooms[room]["members"] if member["sid"] != sid]
        if len(rooms[room]["members"]) <= 0:
            del rooms[room]

    for member in rooms.get(room, {}).get("members", []):
        user_language = member["language"]
        disconnect_message = translator.translate("has left the room", src='auto', dest=user_language).text
        emit("message", {"name": name, "message": disconnect_message}, room=member["sid"])

    print(f"{name} left the room {room}")

@socketio.on("leave")
def leave():
    room = session.get("room")
    name = session.get("name")
    language = session.get("language")
    user_id = session.get("user_id")
    sid = request.sid
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] = [member for member in rooms[room]["members"] if member["sid"] != sid]
        if len(rooms[room]["members"]) <= 0:
            del rooms[room]

    for member in rooms.get(room, {}).get("members", []):
        user_language = member["language"]
        leave_message = translator.translate("has left the room", src='auto', dest=user_language).text
        emit("message", {"name": name, "message": leave_message}, room=member["sid"])

    print(f"{name} left the room {room}")

def notify_server_error(room, message):
    for member in rooms.get(room, {}).get("members", []):
        user_language = member["language"]
        translated_message = translator.translate(message, src='auto', dest=user_language).text
        emit("server_error", {"message": translated_message}, room=member["sid"])

if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 5000))
        socketio.run(app, host='0.0.0.0', port=port)
    except Exception as e:
        for room in rooms:
            notify_server_error(room, "Server encountered an issue. Please leave the room.")
        print("Server encountered an issue:", e)