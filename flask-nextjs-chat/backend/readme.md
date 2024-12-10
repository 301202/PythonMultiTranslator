# Multilingual Chat Application

This repository contains a multilingual chat application built using Flask and Flask-SocketIO. The application allows users to join chat rooms and communicate in different languages, with messages being translated in real-time using Google Translate.

## Features

- Create or join chat rooms with unique codes.
- Real-time messaging with translations based on the user's preferred language.
- Notification messages when users join or leave the chat rooms.
- Cross-Origin Resource Sharing (CORS) enabled for flexibility in frontend integration.

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Steps

1. **Clone the repository**
   - git clone https://github.com/301202/PythonMultiTranslator.git
   - cd multilingual-chat-app

2. **Create a virtual environment and activate it**
    - python -m venv venv
    - source venv/bin/activate  or  venv/Scripts/activate

3. **Install the required packages** 
    - run pip install -r requirements.txt

4. **Create a ".env" file in the root directory and add the following environment variables**
    - FLASK_DEBUG=True
    - SECRET_KEY=your_secret_key
    - PORT=5000

5. **Run your code and navigate to the ip address specified to view it**
    - python app.py
    - http://127.0.0.1:5000

## Usage

### Home Page
- Enter your name.
- Choose to either create a new room or join an existing one using a room code.
- Select your preferred language for translation.

### Chat Room
- Once inside a chat room, you can send messages that will be translated into the preferred languages of other participants in the room.
- Messages sent by others will be translated into your chosen language.

## Code Structure

- **app.py**: The main application file containing all routes and SocketIO events.
- **templates/home.html**: The HTML template for the home page.
- **templates/room.html**: The HTML template for the chat room page.

## Routes

- **/**: The home route where users can create or join a chat room.
- **/room**: The chat room route where users can see and send messages.

## SocketIO Events

- **message**: Handles the sending and receiving of messages, with translation.
- **connect**: Manages user connection to a chat room.
- **disconnect**: Manages user disconnection from a chat room.
- **leave**: Manages user leaving a chat room.

## Dependencies

- Flask
- Flask-SocketIO
- python-dotenv
- googletrans
- Flask-CORS