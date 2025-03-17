import socket
import json
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi


# Load environment variables from the .env.example file
load_dotenv()

# Take the URI from the .env.example file
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables.")

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client.chat_db  # The database's name
collection = db.message  # The collection's name

HOST = "127.0.0.1"
PORT = 5000


def handle_client(conn):
    try:
        data = conn.recv(1024)
        if not data:
            print("Received empty data, closing connection.")
            return

        print("Received raw data:", data)  # Print the raw data

        try:
            message_data = json.loads(data.decode("utf-8"))
            print("Parsed JSON data:", message_data)  # Print the parsed JSON data

            # Save data to MongoDB
            collection.insert_one(message_data)
            print("Saved message:", message_data)
        except json.JSONDecodeError:
            print("Error: Received invalid JSON data.")
        except Exception as e:
            print("Error processing data:", e)
    except Exception as e:
        print("Error handling client connection:", e)
    finally:
        conn.close()
        print("Connection closed.")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Socket server running on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            handle_client(conn)


if __name__ == "__main__":
    start_server()