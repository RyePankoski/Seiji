from typing import Optional, Dict, Any, Callable
import socket
import json
import threading
import queue
from pygame import mixer
import pygame
from piece import Piece  # You'll need to create this file


class NetworkManager:
    def __init__(self, game):
        mixer.init()
        self.socket: Optional[socket.socket] = None
        self.update_queue: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self.connected = False
        self.game = game
        self.enemy_promote_sound = pygame.mixer.Sound("Sounds/enemy_promote.mp3")


    def connect_to_server(self, server_ip: str = "localhost", port: int = 5555) -> bool:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((server_ip, port))
            print("Connected to server!")
            self.connected = True
            threading.Thread(target=self._network_thread, daemon=True).start()
            return True
        except Exception as e:
            print(f"Couldn't connect to server: {e}")
            self.connected = False
            return False

    def send_game_state(self):
        """Serialize and send the current game state"""
        # Convert board to serializable format
        serialized_board = []
        print(f"{self.game.board.i_promoted}")
        for row in self.game.board.board:
            serialized_row = []
            for piece in row:
                if piece is not None:
                    serialized_row.append({
                        "name": piece.name,
                        "movement_squares": piece.movement_squares,
                        "owner": piece.owner,
                        "promoted": piece.promoted
                    })
                else:
                    serialized_row.append(None)
            serialized_board.append(serialized_row)

        monarchs_placed = {
            str(player): placed
            for player, placed in self.game.monarchs_placed.items()
        }

        # Serialize reserves for both players
        serialized_reserves = {
            str(player): [
                {
                    "name": piece.name,
                    "movement_squares": piece.movement_squares,
                    "owner": piece.owner,
                    "promoted": piece.promoted
                }
                for piece in pieces
            ]
            for player, pieces in self.game.reserve_manager.reserves.items()
        }

        game_state = {
            "board": serialized_board,
            "current_player": self.game.current_player,
            "monarchs_placed": monarchs_placed,
            "game_phase": self.game.game_phase,
            "current_state": self.game.current_state,
            "winner": self.game.winner,
            "reserves": serialized_reserves,
            "i_promoted": self.game.board.i_promoted
        }
        print(f"Sent: {monarchs_placed}")

        try:
            state_string = json.dumps(game_state)
            print("Client says: 'Sending data'")
            self.socket.send(state_string.encode())
            return True
        except Exception as e:
            print(f"Error sending game state: {e}")
            self.connected = False
            return False

    def update_game_state(self, new_state):
        """Update the game state based on received network data"""
        try:
            from piece import Piece
            board_data = new_state["board"]
            new_board = []
            for row in board_data:
                new_row = []
                for piece_data in row:
                    if piece_data is not None:
                        piece = Piece(
                            name=piece_data["name"],
                            movement_squares=piece_data["movement_squares"],
                            owner=piece_data["owner"],
                            promoted=piece_data["promoted"]
                        )
                        new_row.append(piece)
                    else:
                        new_row.append(None)
                new_board.append(new_row)

            self.game.board.board = new_board
            self.game.current_player = new_state["current_player"]

            # Convert monarchs_placed back to integer keys
            monarchs_placed = {
                int(player): placed
                for player, placed in new_state["monarchs_placed"].items()
            }
            self.game.monarchs_placed = monarchs_placed

            # Update reserves
            if "reserves" in new_state:
                new_reserves = {}
                for player_str, pieces_data in new_state["reserves"].items():
                    player = int(player_str)
                    new_reserves[player] = []
                    for piece_data in pieces_data:
                        piece = Piece(
                            name=piece_data["name"],
                            movement_squares=piece_data["movement_squares"],
                            owner=piece_data["owner"],
                            promoted=piece_data["promoted"]
                        )
                        new_reserves[player].append(piece)
                self.game.reserve_manager.reserves = new_reserves

            self.game.game_phase = new_state["game_phase"]
            self.game.current_state = new_state["current_state"]
            self.game.winner = new_state["winner"]

            did_enemy_promote = new_state.get("i_promoted", False)
            print(f"{new_state["i_promoted"]}")

            if did_enemy_promote:
                self.enemy_promote_sound.play()
                self.game.i_promoted = False

            print(f"Received: {new_state['current_state']}")

        except Exception as e:
            print(f"Error updating game state: {e}")

    def process_network_updates(self) -> None:
        """Process any pending network updates and apply them to the game state"""
        try:
            while not self.update_queue.empty():
                new_state = self.update_queue.get_nowait()
                with self.lock:
                    self.update_game_state(new_state)
        except queue.Empty:
            pass

    def _network_thread(self) -> None:
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if data:
                    new_state = json.loads(data.decode())
                    print("Client says: 'Pushing received data into queue'")
                    self.update_queue.put(new_state)
            except Exception as e:
                print(f"Network error: {e}")
                self.connected = False
                break

    def disconnect(self) -> None:
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"Error closing socket: {e}")
        self.socket = None
