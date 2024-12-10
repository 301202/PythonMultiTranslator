from flask import Flask, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from googletrans import Translator
from io import BytesIO
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import unicodedata
import os
import random
from string import ascii_uppercase, digits

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

translator = Translator()
rooms = {}  # Stores active rooms and their details
files = {}  # Tracks uploaded files for cleanup


# Utility Functions
def generate_unique_code(length=4):
    """Generate a unique room code."""
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code


def generate_unique_id(length=8):
    """Generate a unique user ID."""
    return ''.join(random.choice(ascii_uppercase + digits) for _ in range(length))


def clean_text(text):
    """Clean and normalize extracted text."""
    text = unicodedata.normalize('NFKD', text)
    replacements = {'•': '-', '–': '-', '—': '-', '�': ''}
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return ' '.join(text.split())


# Routes
@app.route("/api/create-room", methods=["POST"])
def create_room():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    room = generate_unique_code()
    rooms[room] = {"members": [], "messages": []}

    session["room"] = room
    session["name"] = name
    session["user_id"] = generate_unique_id()
    return jsonify({"room": room})


@app.route("/api/join-room", methods=["POST"])
def join_room_api():
    data = request.json
    name = data.get("name")
    code = data.get("code")

    if not name or not code:
        return jsonify({"error": "Name and room code are required"}), 400

    if code not in rooms:
        return jsonify({"error": "Room does not exist"}), 404

    session["room"] = code
    session["name"] = name
    session["user_id"] = generate_unique_id()
    return jsonify({"room": code})


# Socket.IO Handlers
@socketio.on("connect")
def on_connect():
    room = session.get("room")
    name = session.get("name")
    user_id = session.get("user_id")
    sid = request.sid

    if not room or not name:
        return

    if room not in rooms:
        rooms[room] = {"members": [], "messages": []}

    join_room(room)
    rooms[room]["members"].append({"name": name, "sid": sid, "user_id": user_id})

    emit("update_users", {"users": rooms[room]["members"]}, room=room)
    emit("message", {"name": "System", "message": f"{name} has joined the room"}, room=room)


@socketio.on("message")
def on_message(data):
    room = session.get("room")
    name = session.get("name")
    if not room or not name or room not in rooms:
        return

    message = data.get("message")
    rooms[room]["messages"].append({"name": name, "message": message})

    for member in rooms[room]["members"]:
        emit("message", {"name": name, "message": message}, room=member["sid"])


@socketio.on("pdf_upload")
def on_pdf_upload(data):
    room = session.get("room")
    if not room or room not in rooms:
        return

    file_content = BytesIO(data["file"])
    filename = data.get("filename", "uploaded.pdf")
    reader = PdfReader(file_content)

    extracted_text = ""
    for page in reader.pages:
        if page is not None:
            text = clean_text(page.extract_text() or "")
            extracted_text += text + "\n"

    if not extracted_text.strip():
        emit("server_error", {"message": "No text found in the PDF"})
        return

    for member in rooms[room]["members"]:
        user_lang = member.get("language", "en")
        translated_text = translator.translate(extracted_text, dest=user_lang).text
        emit("pdf_content", {"filename": filename, "content": translated_text}, room=member["sid"])


@socketio.on("disconnect")
def on_disconnect():
    room = session.get("room")
    name = session.get("name")
    sid = request.sid

    if room not in rooms:
        return

    rooms[room]["members"] = [m for m in rooms[room]["members"] if m["sid"] != sid]

    if not rooms[room]["members"]:
        del rooms[room]
    else:
        emit("update_users", {"users": rooms[room]["members"]}, room=room)
        emit("message", {"name": "System", "message": f"{name} has left the room"}, room=room)


# Start the application
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 5000)))
