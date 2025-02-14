from constants import *
from piece import Piece
import pygame


class ReserveManager:

    def __init__(self):
        # Initialize reserve pieces for both players
        self.reserves = {
            PLAYER_1: [],
            PLAYER_2: []
        }
        self.selected_piece = None
        self.initialize_reserves()

    def reset_reserves(self):
        self.reserves = {
            PLAYER_1: [],
            PLAYER_2: []
        }
        self.initialize_reserves()

    def initialize_reserves(self):
        for player in [PLAYER_1, PLAYER_2]:
            # Add advisors (2 squares diagonally)
            for _ in range(ADVISOR_NUMBER):
                self.reserves[player].append(
                    Piece("advisor", [(3, 3), (3, -3), (-3, 3), (-3, -3), (2, 2), (2, -2), (-2, 2), (-2, -2), (1, 1), (1, -1), (-1, 1), (-1, -1)], player)
                )

            # Add officials (1 square orthogonally)
            for _ in range(OFFICIAL_NUMBER):
                self.reserves[player].append(
                    Piece("official", [(0, 1), (0, -1), (1, 0), (-1, 0)], player)
                )

            # Add palace pieces
            for _ in range(PALACE_NUMBER):
                self.reserves[player].append(
                    Piece("palace", [], player)
                )

            # Add monarch (same as official - 1 square orthogonally)
            for _ in range(1):
                self.reserves[player].append(
                    Piece("monarch", [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)], player)
                )

            for _ in range(1):
                self.reserves[player].append(
                    Piece("spy", [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)], player)
                )

    def get_pieces(self, player):
        return self.reserves[player]

    def get_all_pieces(self):
        return self.reserves[PLAYER_1], self.reserves[PLAYER_2]

    def remove_piece(self, player, piece_index):
        """Remove a piece from reserve when it's placed on the board"""
        if 0 <= piece_index < len(self.reserves[player]):
            return self.reserves[player].pop(piece_index)
        return None

    def add_piece(self, piece):
        self.reserves[piece.owner].append(piece)

    def is_click_in_reserve(self, player, mouse_pos, display_manager):
        """Convert screen coordinates to reserve area check"""
        current_width, current_height = display_manager.get_dimensions()

        # Calculate board rect for reference
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        # Calculate reserve dimensions
        reserve_width = int(current_width * 0.2)
        reserve_height = int(current_height * 0.3)
        table_size = max(reserve_width, reserve_height)
        reserve_start_x = grid_rect.right + int(current_width * 0.02)

        # Create reserve rect based on player
        if player == PLAYER_1:
            reserve_rect = pygame.Rect(reserve_start_x, grid_rect.top, table_size, table_size)
        else:
            reserve_rect = pygame.Rect(reserve_start_x, grid_rect.bottom - table_size, table_size, table_size)

        # Check if click is in reserve area
        if not reserve_rect.collidepoint(mouse_pos):
            return None

        return reserve_rect

    def get_piece_at_position(self, player, click_x, click_y, current_width, current_height):
        pieces = self.get_pieces(player)
        if not pieces:
            return None

        # Calculate grid rect same way as draw_reserve_pieces
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        # Calculate reserve table dimensions
        reserve_width = int(current_width * 0.2)
        reserve_height = int(current_height * 0.3)
        table_size = max(reserve_width, reserve_height)
        reserve_start_x = grid_rect.right + int(current_width * 0.02)

        piece_size = 80
        spacing = 10
        click_point = pygame.math.Vector2(click_x, click_y)
        positions = []

        # Starting position based on player
        x = reserve_start_x
        y = grid_rect.top if player == PLAYER_1 else grid_rect.bottom - table_size

        for _ in range(len(pieces)):
            positions.append((x, y))
            x += piece_size + spacing
            if x + piece_size > reserve_start_x + table_size:
                x = reserve_start_x
                y += piece_size + spacing

        for i, pos in enumerate(positions):
            if i < len(pieces):
                piece_rect = pygame.Rect(pos[0], pos[1], piece_size, piece_size)
                if piece_rect.collidepoint(click_point):
                    return pieces[i]
