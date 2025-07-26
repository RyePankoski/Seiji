import pygame
from sound_manager import SoundManager


class Board:
    def __init__(self, size, game):
        SoundManager()
        self.game = game
        self.size = size
        self.board = [[None for x in range(size)] for y in range(size)]
        self.i_promoted = False

    def get_size(self) -> int:
        return self.size

    def wipe_board(self):
        size = self.get_size()
        self.board = [[None for x in range(size)] for y in range(size)]

    def get_adjacent_pieces(self, position) -> dict[str, list[None]]:
        x, y = position
        adjacent_pieces = {}

        # Define positions with their labels
        adjacent_positions = {
            'up': (x, y - 1),
            'down': (x, y + 1),
            'left': (x - 1, y),
            'right': (x + 1, y)
        }

        for direction, adj_pos in adjacent_positions.items():
            if self.is_valid_position(adj_pos):
                piece = self.get_piece(adj_pos)
                if piece is not None:
                    adjacent_pieces[direction] = piece

        return adjacent_pieces

    def handle_status(self, piece, adjacent_pieces):
        DEFAULT_MOVEMENTS = {
            "monarch": ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)),
            "advisor": ((3, 3), (3, -3), (-3, 3), (-3, -3), (2, 2), (2, -2), (-2, 2), (-2, -2), (1, 1), (1, -1),
                        (-1, 1), (-1, -1)),
            "official": ((0, 1), (0, -1), (1, 0), (-1, 0))
        }

        # If no adjacent pieces, demote and reset movements
        if not adjacent_pieces:
            if piece.promoted:
                piece.promoted = False
                piece.movement_squares = DEFAULT_MOVEMENTS[piece.name]
            return

        if piece.promoted:
            if piece.name == "advisor":
                has_friendly_monarch = any(
                    p.name == "monarch" and p.owner == piece.owner for p in adjacent_pieces.values())
                if not has_friendly_monarch:
                    piece.promoted = False
                    piece.movement_squares = DEFAULT_MOVEMENTS["advisor"]
            if piece.name == "official":
                if any(p.name == "monarch" and p.owner == piece.owner for p in adjacent_pieces.values()):
                    piece.movement_squares = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
                elif any(p.name == "advisor" and p.owner == piece.owner for p in adjacent_pieces.values()):
                    piece.movement_squares = ((0, 1), (0, -1), (1, 0), (-1, 0), (0, 2), (0, -2), (2, 0), (-2, 0))
                else:
                    piece.promoted = False
                    piece.movement_squares = DEFAULT_MOVEMENTS["official"]
            return

        else:
            if piece.name == "monarch":
                # Check for adjacent friendly pieces (excluding enemy pieces) and no friendly palaces
                has_only_friendly_adjacent = all(p.owner == piece.owner for p in adjacent_pieces.values())
                has_any_friendly_adjacent = any(p.owner == piece.owner for p in adjacent_pieces.values())
                has_friendly_palace = any(
                    p.name == "palace" and p.owner == piece.owner for p in adjacent_pieces.values())

                # Only promote if there are friendly pieces, no enemy pieces, and no friendly palace
                if has_only_friendly_adjacent and has_any_friendly_adjacent and not has_friendly_palace:
                    SoundManager.play_sound('promote')
                    self.i_promoted = True
                    piece.promoted = True
                    piece.movement_squares = ((2, 2), (2, -2), (-2, 2), (-2, -2), (0, 2), (0, -2), (2, 0), (-2, 0),
                                              (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
            elif piece.name == "advisor":
                has_friendly_monarch = any(
                    p.name == "monarch" and p.owner == piece.owner for p in adjacent_pieces.values())
                if has_friendly_monarch:
                    SoundManager.play_sound('promote')
                    self.i_promoted = True
                    piece.promoted = True
                    piece.movement_squares = ((2, 2), (2, -2), (-2, 2), (-2, -2), (0, 2), (0, -2), (2, 0), (-2, 0),
                                              (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
            elif piece.name == "official":
                if any(p.name == "monarch" and p.owner == piece.owner for p in adjacent_pieces.values()):
                    SoundManager.play_sound('promote')
                    self.i_promoted = True
                    piece.promoted = True
                    piece.movement_squares = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))
                elif any(p.name == "advisor" and p.owner == piece.owner for p in adjacent_pieces.values()):
                    SoundManager.play_sound('promote')
                    self.i_promoted = True

                    piece.promoted = True
                    piece.movement_squares = ((0, 1), (0, -1), (1, 0), (-1, 0), (0, 2), (0, -2), (2, 0), (-2, 0))

    def check_all_pieces_status(self):
        self.i_promoted = False
        for y in range(self.size):
            for x in range(self.size):
                self._check_piece_at_position(x, y)

    def _check_piece_at_position(self, x, y):
        current_piece = self.get_piece((x, y))
        if current_piece is not None:
            adjacent_pieces = self.get_adjacent_pieces((x, y))
            if adjacent_pieces is not None:
                self.handle_status(current_piece, adjacent_pieces)

    def get_board_position(self, mouse_pos, display_manager):
        current_width, current_height = display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / self.size
        board_pixels = self.size * cell_size

        # Calculate board rect
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        # If click is outside board, return None
        if not grid_rect.collidepoint(mouse_pos):
            return None

        # Calculate board coordinates
        board_x = int((mouse_pos[0] - grid_rect.left) / cell_size)
        board_y = int((mouse_pos[1] - grid_rect.top) / cell_size)

        # Ensure coordinates are within bounds
        if 0 <= board_x < self.size and 0 <= board_y < self.size:
            return (board_x, board_y)
        return None

    def place_piece(self, piece, position):
        x, y = position
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False

        if self.board[y][x] is not None:
            return False

        self.board[y][x] = piece
        return True

    def remove_piece(self, position):
        """Remove and return piece at position"""
        x, y = position
        if 0 <= x < self.size and 0 <= y < self.size:
            piece = self.board[y][x]
            self.board[y][x] = None
            return piece
        return None

    def get_piece(self, position):
        x, y = position
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.board[y][x]
        return None

    def is_valid_position(self, position):
        """Check if a position is valid on the board"""
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size

    def get_grid_rect(self, display_manager):
        """Get the board's rectangle in screen coordinates"""
        current_width, current_height = display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / self.size
        board_pixels = self.size * cell_size

        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)
        return grid_rect, cell_size

    def resize_board(self, new_size):
        """Resize the board and recreate the array"""
        self.size = new_size
        self.board = [[None for x in range(new_size)] for y in range(new_size)]
