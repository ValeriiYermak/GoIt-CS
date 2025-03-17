import socket
import json
import os
import multiprocessing
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

# Download environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables.")

# Connect to MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client.chat_db
collection = db.message

# Server settings
HTTP_HOST, HTTP_PORT = "0.0.0.0", 3000
SOCKET_HOST, SOCKET_PORT = "127.0.0.1", 5000


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Requested path: {self.path}")
        if self.path == "/":
            self.path = "index.html"
        elif self.path == "/index.html":
            self.path = "index.html"
        elif self.path == "/message.html":
            self.path = "message.html"
        elif self.path == "/style.css":
            self.path = "style.css"
        elif self.path == "/logo.png":
            self.path = "logo.png"
        elif self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
        else:
            self.path = "error.html"
            self.send_response(404)
            print(f"File {self.path} not found")
            self.end_headers()
            self.wfile.write(b"Page not found")
            return

        # Check if the file exists
        if not os.path.exists(self.path):
            print(f"File {self.path} does not exist")
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")
            return

        try:
            # Open and read the file
            with open(self.path, "rb") as file:
                self.send_response(200)
                if self.path.endswith(".html"):
                    self.send_header("Content-type", "text/html")
                elif self.path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif self.path.endswith(".png"):
                    self.send_header("Content-type", "image/png")
                self.end_headers()
                self.wfile.write(file.read())
        except Exception as e:
            print(f"Error during request handling: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

    def do_POST(self):
        if self.path == "/message.html":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_error(400, "No data received")
                return

            post_data = self.rfile.read(content_length).decode("utf-8")
            form_data = parse_qs(post_data)

            username = form_data.get("username", [""])[0].strip()
            message = form_data.get("message", [""])[0].strip()

            if username and message:
                data = {
                    "username": username,
                    "message": message,
                    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f"),
                }

                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((SOCKET_HOST, SOCKET_PORT))
                        sock.sendall(json.dumps(data).encode("utf-8"))
                except Exception as e:
                    print(f"Failed to send data to Socket server: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Failed to send data to Socket server")
                    return

                os.makedirs("storage", exist_ok=True)
                try:
                    with open("storage/data.json", "a", encoding="utf-8") as f:
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    print("Data saved to file")
                except Exception as e:
                    print(f"Failed to save data to file: {e}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Failed to save data to file")
                    return

                # Redirect to message.html
                self.send_response(303)
                self.send_header("Location", "/message.html")
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid form data")


def run_http_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer((HTTP_HOST, HTTP_PORT), CustomHandler)
    print(f"Running web server on {HTTP_HOST}:{HTTP_PORT}")
    server.serve_forever()


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
        server.bind(("0.0.0.0", SOCKET_PORT))
        server.listen()
        print(f"Socket server running on 0.0.0.0:{SOCKET_PORT}")

        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            handle_client(conn)


if __name__ == "__main__":
    http_process = multiprocessing.Process(target=run_http_server)
    socket_process = multiprocessing.Process(target=start_server)

    http_process.start()
    socket_process.start()

    http_process.join()
    socket_process.join()
