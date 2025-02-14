import socket
import threading
import json
import queue


class GameServer:
    def __init__(self):
        self.clients = []  # List to store client connections
        self.game_states = {}  # Dictionary to store game states for each client
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        print(f"New client connected: {addr}")

        with self.lock:
            self.clients.append(conn)
            client_id = len(self.clients) - 1
        print(f"Assigned client ID: {client_id}")

        try:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        print(f"Client {addr} disconnected gracefully")
                        break

                    print(f"Received {len(data)} bytes from client {addr}")
                    game_state = json.loads(data.decode())

                    with self.lock:
                        self.game_states[client_id] = game_state
                        # Broadcast to other clients
                        for i, client in enumerate(self.clients):
                            if i != client_id:
                                try:
                                    print(f"Sending update to client {i}")
                                    client.send(data)
                                    print(f"Successfully sent to client {i}")
                                except socket.error as e:
                                    print(f"Failed to send to client {i}: {str(e)}")
                                    # Remove dead client
                                    self.clients.remove(client)
                                    if i in self.game_states:
                                        del self.game_states[i]

                except socket.error as e:
                    print(f"Socket error with client {addr}: {str(e)}")
                    break
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON from client {addr}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Unexpected error handling client {addr}: {str(e)}")
                    break

        finally:
            print(f"Cleaning up connection for client {addr}")
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
                if client_id in self.game_states:
                    del self.game_states[client_id]
            conn.close()
            print(f"Cleaned up client {addr}")

    def start(self, host='0.0.0.0', port=5555):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Bind to all available interfaces
            server.bind((host, port))
            server.listen()
            print(f"Server is listening on {host}:{port}")

            while True:
                try:
                    conn, addr = server.accept()
                    print(f"New connection from {addr}")

                    # Only allow 2 players
                    if len(self.clients) < 2:
                        thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                        thread.start()
                        print(f"Active connections: {len(self.clients)}")
                    else:
                        print(f"Rejected connection from {addr}: game full")
                        conn.close()
                except socket.error as e:
                    print(f"Error accepting connection: {e}")
                    continue

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            print("Server shutting down...")
            server.close()


if __name__ == "__main__":
    server = GameServer()
    server.start(host='0.0.0.0', port=5555)
