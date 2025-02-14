import pygame
from constants import *
from star_field import MenuStarfield
from board import Board
import math
from movement_patterns import get_valid_moves


# from menu import Menu


class DrawUtilities:
    """Base class for drawing utilities"""

    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.board = Board

    def draw(self, screen):
        pass

    def handle_resize(self):
        pass

    def fade_to_black(self, screen, speed=5):
        """Create a fade to black transition effect"""
        fade_surface = pygame.Surface((BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255, speed):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(5)


class MenuDrawUtilities:

    def __init__(self, display_manager, menu):
        self.display_manager = display_manager
        self.menu = menu

        self.starfield_config = {
            'max_stars': 200,
            'speed': 3,
            'spawn_interval': 3,
            'colored_star_chance': 2,
            'max_star_size': 10,
            'background_color': (0, 0, 0)
        }

        current_width, current_height = self.display_manager.get_dimensions()
        self.starfield = MenuStarfield(current_width, current_height, self.starfield_config)

        self.title_font = pygame.font.Font("Fonts/font.otf", 200)
        self.button_font = pygame.font.Font("Fonts/general_text.ttf", 40)
        self.input_font = pygame.font.Font(None, 40)

    def draw(self, screen):
        current_width, current_height = self.display_manager.get_dimensions()

        screen.fill(self.starfield_config['background_color'])

        self.starfield.update()
        self.starfield.draw(screen)

        self._draw_title(screen)
        self._draw_buttons(screen)

        if self.menu.show_ip_dialog:
            self._draw_ip_dialog(screen)

        if self.menu.show_setup_dialog:
            self._draw_setup_dialog(screen)

    def _draw_setup_dialog(self, screen):
        """Draw the setup dialog for board size configuration"""
        current_width, current_height = self.display_manager.get_dimensions()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Dialog dimensions
        dialog_width = 400
        dialog_height = 200
        dialog_x = (current_width - dialog_width) // 2
        dialog_y = (current_height - dialog_height) // 2

        # Draw dialog box
        pygame.draw.rect(screen, (0, 0, 0),
                         (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, (255, 255, 255),
                         (dialog_x, dialog_y, dialog_width, dialog_height), 2)

        # Draw dialog title
        title = self.button_font.render("Enter Board Size", True, (255, 255, 255))
        screen.blit(title, (dialog_x + 20, dialog_y + 20))

        # Draw input box
        input_box = pygame.Rect(dialog_x + 20, dialog_y + 70, dialog_width - 40, 40)
        pygame.draw.rect(screen, (50, 50, 50), input_box)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)

        # Draw input text
        input_text = self.input_font.render(self.menu.board_size_input, True, (255, 255, 255))
        screen.blit(input_text, (input_box.x + 5, input_box.y + 10))

        # Draw hint text
        hint = self.input_font.render("Press Enter to confirm", True, (200, 200, 200))
        hint_rect = hint.get_rect(centerx=dialog_x + dialog_width // 2,
                                  bottom=dialog_y + dialog_height - 20)
        screen.blit(hint, hint_rect)

    def handle_resize(self):
        current_width, current_height = self.display_manager.get_dimensions()
        self.starfield = MenuStarfield(current_width, current_height, self.starfield_config)

    def _draw_title(self, screen):
        current_width, current_height = self.display_manager.get_dimensions()
        title_text = self.title_font.render("Seiji", True, GOLD)
        title_rect = title_text.get_rect(centerx=current_width // 2, top=50)
        screen.blit(title_text, title_rect)

    def _draw_buttons(self, screen):
        for i, (button_rect, text) in enumerate(self.menu.buttons):
            border_rect = self.menu.button_borders[i]

            # Draw button background and border
            pygame.draw.rect(screen, (0, 0, 0), button_rect)
            pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)

            # Highlight selected button
            if i == self.menu.selected_button:
                pygame.draw.rect(screen, (50, 50, 50), button_rect)

            # Draw button text
            text_surface = self.button_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

    def _draw_ip_dialog(self, screen):
        """Draw the IP input dialog"""
        current_width, current_height = self.display_manager.get_dimensions()

        # Draw semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Dialog dimensions
        dialog_width = 400
        dialog_height = 200
        dialog_x = (current_width - dialog_width) // 2
        dialog_y = (current_height - dialog_height) // 2

        # Draw dialog box
        pygame.draw.rect(screen, (0, 0, 0),
                         (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, (255, 255, 255),
                         (dialog_x, dialog_y, dialog_width, dialog_height), 2)

        # Draw dialog title
        title = self.button_font.render("Enter Server IP", True, (255, 255, 255))
        screen.blit(title, (dialog_x + 20, dialog_y + 20))

        # Draw input box
        input_box = pygame.Rect(dialog_x + 20, dialog_y + 70, dialog_width - 40, 40)
        pygame.draw.rect(screen, (50, 50, 50), input_box)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)

        # Draw input text
        input_text = self.input_font.render(self.menu.ip_input, True, (255, 255, 255))
        screen.blit(input_text, (input_box.x + 5, input_box.y + 10))


class GameDrawUtilities:

    def __init__(self, display_manager, board, starfield_config=None, ):
        self.title_font = pygame.font.Font("Fonts/font.otf", 200)
        self.button_font = pygame.font.Font("Fonts/general_text.ttf", 50)
        self.display_manager = display_manager
        self.board = board

        self.default_starfield_config = {
            'max_stars': 200,
            'speed': 1,
            'spawn_interval': 10,
            'colored_star_chance': 2,
            'max_star_size': 10,
            'background_color': (5, 5, 15)
        }

        self.resign_button_color = (200, 0, 0)  # Dark red color
        self.resign_button_hover_color = (100, 34, 34)  # Lighter red for hover
        self.resign_button_rect = None  # Will be updated in draw_resign_button
        self.resign_button_active = False

        self.starfield_config = starfield_config or self.default_starfield_config
        current_width, current_height = self.display_manager.get_dimensions()
        self.starfield = MenuStarfield(current_width, current_height, self.starfield_config)
        self.board_texture = pygame.image.load("Textures/background.png")
        self.board_texture = pygame.transform.scale(self.board_texture,
                                                    (BOARD_SIZE * BASE_CELL_SIZE,
                                                     BOARD_SIZE * BASE_CELL_SIZE))
        self.table_texture = pygame.image.load("Textures/tables.png").convert_alpha()

    def draw(self, screen, valid_placements, valid_moves=None, game_phase="playing"):

        self.starfield.update()
        self.starfield.draw(screen)
        self.draw_board(screen)
        self.draw_reserve_tables(screen)
        self.draw_resign_button(screen)

        # Draw center square highlight during monarch placement
        if game_phase == "monarch_placement":
            self.draw_center_highlight(screen)

        if valid_moves:
            self.draw_move_highlights(screen, valid_moves)

        if valid_placements:
            self.draw_move_highlights(screen, valid_placements)

        self.draw_board_pieces(screen)

    def draw_game_over_screen(self, screen, current_player):
        if current_player == PLAYER_1:
            winner = "BLACK"
        else:
            winner = "WHITE"

        current_width, current_height = self.display_manager.get_dimensions()

        # First render the black shadow text
        shadow_text = self.title_font.render(f"{winner} WINS!", True, (0, 0, 0))
        # Then render the main golden text
        win_text = self.title_font.render(f"{winner} WINS!", True, GOLD)

        # Get the rectangle of the text
        text_rect = win_text.get_rect()
        text_rect.center = (current_width // 2, current_height // 2 - 50)

        # Draw the shadow slightly offset down and right
        shadow_rect = text_rect.copy()
        shadow_rect.x += 4  # Offset right
        shadow_rect.y += 4  # Offset down
        screen.blit(shadow_text, shadow_rect)

        # Draw the main golden text on top
        screen.blit(win_text, text_rect)

        # Draw Menu button
        menu_text = self.button_font.render("MENU", True, (0, 0, 0))
        menu_shadow = self.button_font.render("MENU", True, (0, 0, 0))
        menu_rect = menu_text.get_rect()
        menu_rect.center = (current_width // 2 - 120, current_height // 2 + 70)

        # Menu button shadow and background
        padding = 15
        pygame.draw.rect(screen, (0, 0, 0), (
            menu_rect.x - padding + 4, menu_rect.y - padding + 4, menu_rect.width + padding * 2,
            menu_rect.height + padding * 2), border_radius=8)  # Shadow
        pygame.draw.rect(screen, GOLD, (
            menu_rect.x - padding, menu_rect.y - padding, menu_rect.width + padding * 2,
            menu_rect.height + padding * 2),
                         border_radius=8)  # Background

        # Draw menu text with shadow
        shadow_menu_rect = menu_rect.copy()
        shadow_menu_rect.x += 2
        shadow_menu_rect.y += 2
        screen.blit(menu_shadow, shadow_menu_rect)
        screen.blit(menu_text, menu_rect)

        # Draw Rematch button
        rematch_text = self.button_font.render("REMATCH", True, (0, 0, 0))
        rematch_shadow = self.button_font.render("REMATCH", True, (0, 0, 0))
        rematch_rect = rematch_text.get_rect()
        rematch_rect.center = (current_width // 2 + 120, current_height // 2 + 70)

        # Rematch button shadow and background
        pygame.draw.rect(screen, (0, 0, 0), (
            rematch_rect.x - padding + 4, rematch_rect.y - padding + 4, rematch_rect.width + padding * 2,
            rematch_rect.height + padding * 2), border_radius=8)  # Shadow
        pygame.draw.rect(screen, GOLD, (
            rematch_rect.x - padding, rematch_rect.y - padding, rematch_rect.width + padding * 2,
            rematch_rect.height + padding * 2), border_radius=8)  # Background

        # Draw rematch text with shadow
        shadow_rematch_rect = rematch_rect.copy()
        shadow_rematch_rect.x += 2
        shadow_rematch_rect.y += 2
        screen.blit(rematch_shadow, shadow_rematch_rect)
        screen.blit(rematch_text, rematch_rect)

        return menu_rect, rematch_rect  # Return the button rects for click detection

    def draw_resign_button(self, screen):
        current_width, current_height = self.display_manager.get_dimensions()

        # Button dimensions and position
        button_width = 160
        button_height = 50
        margin = 20

        # Create button rectangle
        self.resign_button_rect = pygame.Rect(
            margin,  # x position
            margin,  # y position
            button_width,
            button_height
        )

        # Draw button background
        button_color = self.resign_button_hover_color if self.resign_button_active else self.resign_button_color
        pygame.draw.rect(screen, button_color, self.resign_button_rect)
        pygame.draw.rect(screen, GOLD, self.resign_button_rect, 2)  # Gold border

        # Draw button text
        text = self.button_font.render("Resign", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.resign_button_rect.center)
        screen.blit(text, text_rect)
        self.handle_resign_hover()

    def handle_resign_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.resign_button_rect:
            self.resign_button_active = self.resign_button_rect.collidepoint(mouse_pos)
        return self.resign_button_active

    def draw_center_highlight(self, screen):
        """Draw a red highlight on the center square"""
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        # Calculate center square position
        center = BOARD_SIZE // 2
        center_x = grid_rect.left + center * cell_size
        center_y = grid_rect.top + center * cell_size

        # Create highlight surface
        highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 0, 0, 128), highlight.get_rect())  # Red with some transparency
        screen.blit(highlight, (center_x, center_y))

    def draw_move_highlights(self, screen, squares, is_placement=False):
        """Draw highlights for valid moves or placements"""
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        for x, y in squares:
            # Calculate position on screen
            screen_x = grid_rect.left + x * cell_size
            screen_y = grid_rect.top + y * cell_size

            # Create highlight surface
            highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)

            if is_placement:
                # Always green for placement squares
                pygame.draw.rect(highlight, (0, 255, 0, 100), highlight.get_rect())
            else:
                # Check if there's a piece at this position (capture highlight)
                if self.board.get_piece((x, y)) is not None:
                    pygame.draw.rect(highlight, (255, 0, 0, 100), highlight.get_rect())  # Red for capture
                else:
                    pygame.draw.rect(highlight, (0, 255, 0, 100), highlight.get_rect())  # Green for movement

            screen.blit(highlight, (screen_x, screen_y))

    def draw_board(self, screen):
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        border_width = int(current_height * 0.008)
        self._draw_board_borders(screen, grid_rect, border_width)

        board_background = pygame.transform.scale(self.board_texture, (board_pixels, board_pixels))
        screen.blit(board_background, grid_rect)

        self._draw_grid_lines(screen, grid_rect, cell_size)
        self._draw_center_x(screen, grid_rect, cell_size)
        self._draw_coordinates(screen, grid_rect, cell_size)

    def draw_board_pieces(self, screen):
        """Draw all pieces currently on the board"""
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        # Iterate through the board and draw pieces
        for y in range(self.board.size):
            for x in range(self.board.size):
                piece = self.board.board[y][x]
                if piece:
                    # Calculate piece position on screen
                    piece_x = grid_rect.left + x * cell_size
                    piece_y = grid_rect.top + y * cell_size
                    self.draw_piece(screen, piece, piece_x, piece_y, cell_size)

                    # Draw red circle around promoted pieces
                    if piece.promoted:
                        circle_rect = pygame.Rect(piece_x, piece_y, cell_size, cell_size)
                        pygame.draw.circle(screen,
                                           (255, 50, 0),  # Red color
                                           circle_rect.center,
                                           cell_size * 0.42,  # Slightly smaller than cell
                                           2)  # Line width

    def draw_reserve_tables(self, screen):
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        reserve_width = int(current_width * 0.2)
        reserve_height = int(current_height * 0.3)
        table_size = max(reserve_width, reserve_height)
        reserve_start_x = grid_rect.right + int(current_width * 0.02)

        for y_offset in [grid_rect.top, grid_rect.bottom - table_size]:
            self._draw_table(screen, reserve_start_x, y_offset, table_size, current_height)

    def handle_resize(self):
        current_width, current_height = self.display_manager.get_dimensions()
        self.starfield = MenuStarfield(current_width, current_height, self.starfield_config)

    def _draw_board_borders(self, screen, grid_rect, border_width):
        pygame.draw.rect(screen, (40, 40, 40),
                         (grid_rect.left - border_width,
                          grid_rect.top - border_width,
                          grid_rect.width + border_width * 2,
                          grid_rect.height + border_width * 2))

        pygame.draw.rect(screen, (200, 200, 200),
                         (grid_rect.left - border_width // 2,
                          grid_rect.top - border_width // 2,
                          grid_rect.width + border_width,
                          grid_rect.height + border_width))

    def _draw_grid_lines(self, screen, grid_rect, cell_size):
        for i in range(BOARD_SIZE + 1):
            x = grid_rect.left + i * cell_size
            pygame.draw.line(screen, GRID_COLOR,
                             (x, grid_rect.top),
                             (x, grid_rect.bottom))

            y = grid_rect.top + i * cell_size
            pygame.draw.line(screen, GRID_COLOR,
                             (grid_rect.left, y),
                             (grid_rect.right, y))

    def _draw_center_x(self, screen, grid_rect, cell_size):
        center_x = grid_rect.left + (BOARD_SIZE // 2) * cell_size
        center_y = grid_rect.top + (BOARD_SIZE // 2) * cell_size
        pygame.draw.line(screen, GRID_COLOR,
                         (center_x, center_y),
                         (center_x + cell_size, center_y + cell_size),
                         width=2)
        pygame.draw.line(screen, GRID_COLOR,
                         (center_x + cell_size, center_y),
                         (center_x, center_y + cell_size),
                         width=2)

    def _draw_coordinates(self, screen, grid_rect, cell_size):
        font = pygame.font.Font(None, int(cell_size * 0.5))
        padding = cell_size * 0.3

        for i in range(BOARD_SIZE):
            bottom_number = str(i + 1)
            text = font.render(bottom_number, True, GOLD)
            x = grid_rect.left + (i * cell_size) + (cell_size - text.get_width()) // 2
            y = grid_rect.bottom + padding
            screen.blit(text, (x, y))

            left_number = str(BOARD_SIZE - i)
            text = font.render(left_number, True, GOLD)
            x = grid_rect.left - padding - text.get_width()
            y = grid_rect.top + (i * cell_size) + (cell_size - text.get_height()) // 2
            screen.blit(text, (x, y))

    def _draw_table(self, screen, x, y, size, current_height):
        border_width = int(current_height * 0.008)

        pygame.draw.rect(screen, (40, 40, 40),
                         (x - border_width,
                          y - border_width,
                          size + border_width * 2,
                          size + border_width * 2))

        pygame.draw.rect(screen, (200, 200, 200),
                         (x - border_width // 2,
                          y - border_width // 2,
                          size + border_width,
                          size + border_width))

        table_texture = pygame.transform.scale(self.table_texture, (size, size))
        screen.blit(table_texture, (x, y))

    def draw_reserve_pieces(self, screen, reserve_manager, selected_piece=None):
        current_width, current_height = self.display_manager.get_dimensions()
        desired_board_height = current_height * 0.8
        cell_size = desired_board_height / BOARD_SIZE
        board_pixels = BOARD_SIZE * cell_size
        grid_rect = pygame.Rect(0, 0, board_pixels, board_pixels)
        grid_rect.center = (current_width // 2, current_height // 2)

        reserve_width = int(current_width * 0.2)
        reserve_height = int(current_height * 0.3)
        table_size = max(reserve_width, reserve_height)
        reserve_start_x = grid_rect.right + int(current_width * 0.02)

        piece_size = 80
        spacing = 10
        x = reserve_start_x
        y = grid_rect.top

        # Player 1's pieces (top table)
        player_1_reserve, player_2_reserve = reserve_manager.get_all_pieces()

        for piece in player_1_reserve:
            is_selected = selected_piece and piece == selected_piece
            self.draw_piece(screen, piece, x, y, piece_size)

            if is_selected:
                # Draw selection highlight
                highlight_size = int(piece_size // 2 + 8)
                highlight_color = (255, 255, 0, 100)  # Semi-transparent yellow
                highlight_surface = pygame.Surface((piece_size + 16, piece_size + 16), pygame.SRCALPHA)
                pygame.draw.circle(highlight_surface, highlight_color,
                                   (piece_size // 2 + 8, piece_size // 2 + 8), highlight_size)
                screen.blit(highlight_surface, (x - 8, y - 8))

                # Draw pulsing outer ring
                glow_color = (255, 215, 0)  # Golden glow
                pygame.draw.circle(screen, glow_color,
                                   (int(x + piece_size // 2), int(y + piece_size // 2)),
                                   int(piece_size // 2 + 4), 2)

            x += piece_size + spacing
            if x + piece_size > reserve_start_x + table_size:  # If we hit the edge
                x = reserve_start_x  # Reset to start of row
                y += piece_size + spacing

        x = reserve_start_x
        y = grid_rect.bottom - table_size

        for piece in player_2_reserve:
            # Check if this piece is selected
            is_selected = selected_piece and piece == selected_piece
            self.draw_piece(screen, piece, x, y, piece_size)

            if is_selected:
                # Draw selection highlight
                highlight_size = int(piece_size // 2 + 8)
                highlight_color = (255, 255, 0, 100)  # Semi-transparent yellow
                highlight_surface = pygame.Surface((piece_size + 16, piece_size + 16), pygame.SRCALPHA)
                pygame.draw.circle(highlight_surface, highlight_color,
                                   (piece_size // 2 + 8, piece_size // 2 + 8), highlight_size)
                screen.blit(highlight_surface, (x - 8, y - 8))

                # Draw pulsing outer ring
                glow_color = (255, 215, 0)  # Golden glow
                pygame.draw.circle(screen, glow_color,
                                   (int(x + piece_size // 2), int(y + piece_size // 2)),
                                   int(piece_size // 2 + 4), 2)

            x += piece_size + spacing
            if x + piece_size > reserve_start_x + table_size:  # If we hit the edge
                x = reserve_start_x  # Reset to start of row
                y += piece_size + spacing

    def draw_piece(self, screen, piece, x, y, size):
        # Draw piece background circle
        color = PLAYER_1_COLOR if piece.owner == PLAYER_1 else PLAYER_2_COLOR
        pygame.draw.circle(screen, color, (int(x + size // 2), int(y + size // 2)), int(size // 2 - 4))

        # Draw piece border
        pygame.draw.circle(screen, GOLD, (int(x + size // 2), int(y + size // 2)), int(size // 2 - 4), 2)

        # Draw piece type indicator
        if piece.name == "advisor":
            self._draw_advisor_symbol(screen, x, y, size, piece.owner)
        elif piece.name == "official":
            self._draw_official_symbol(screen, x, y, size, piece.owner)
        elif piece.name == "palace":
            self._draw_palace_symbol(screen, x, y, size, piece.owner)
        elif piece.name == "monarch":
            self._draw_monarch_symbol(screen, x, y, size, piece.owner)
        elif piece.name == "spy":
            self._draw_spy_symbol(screen, x, y, size, piece.owner)

    def _draw_advisor_symbol(self, screen, x, y, size, owner):
        """Draw advisor piece symbol (triangle with dot on top)"""
        color = BLACK if owner == PLAYER_1 else WHITE
        center_x = int(x + size // 2)
        center_y = int(y + size // 2)
        symbol_size = int(size // 2.5)

        # Draw triangle
        triangle_points = [
            (center_x, center_y - symbol_size // 2),  # Top point
            (center_x - symbol_size // 2, center_y + symbol_size // 2),  # Bottom left
            (center_x + symbol_size // 2, center_y + symbol_size // 2)  # Bottom right
        ]
        pygame.draw.lines(screen, color, True, triangle_points, 2)

        # Draw dot at the top point
        dot_radius = symbol_size // 2

        pygame.draw.circle(screen, color,
                           (center_x + 1, center_y - symbol_size // 2),
                           dot_radius, 2)

    def _draw_official_symbol(self, screen, x, y, size, owner):
        """Draw official piece symbol"""
        color = BLACK if owner == PLAYER_1 else WHITE
        center_x = int(x + size // 2)
        center_y = int(y + size // 2)
        radius = int(size // 4)

        # Draw an 'O' shape
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 2)

    def _draw_palace_symbol(self, screen, x, y, size, owner):
        """Draw palace piece symbol (nested squares with center)"""
        color = BLACK if owner == PLAYER_1 else WHITE
        center_x = int(x + size // 2)
        center_y = int(y + size // 2)
        symbol_size = int(size // 2.5)  # Slightly larger symbol

        # Draw outer square rotated 45 degrees (diamond)
        diamond_points = [
            (center_x, center_y - symbol_size),  # Top
            (center_x + symbol_size, center_y),  # Right
            (center_x, center_y + symbol_size),  # Bottom
            (center_x - symbol_size, center_y)  # Left
        ]
        pygame.draw.polygon(screen, color, diamond_points, 2)

        # Draw inner square (straight orientation)
        inner_size = symbol_size // 1.5
        square_points = [
            (center_x - inner_size, center_y - inner_size),  # Top left
            (center_x + inner_size, center_y - inner_size),  # Top right
            (center_x + inner_size, center_y + inner_size),  # Bottom right
            (center_x - inner_size, center_y + inner_size)  # Bottom left
        ]
        pygame.draw.polygon(screen, color, square_points, 2)

        # Draw small circle in center
        center_dot_radius = symbol_size // 4
        pygame.draw.circle(screen, color, (center_x, center_y), center_dot_radius, 1)

    def _draw_monarch_symbol(self, screen, x, y, size, owner):
        """Draw monarch piece symbol (intricate star)"""
        color = BLACK if owner == PLAYER_1 else WHITE
        center_x = int(x + size // 2)
        center_y = int(y + size // 2)
        symbol_size = int(size // 3)

        # Calculate points for an 8-pointed star
        points = []
        num_points = 6
        inner_radius = symbol_size // 2
        outer_radius = symbol_size

        for i in range(num_points * 2):
            angle = (2 * math.pi * i) / (num_points * 2)
            radius = outer_radius if i % 2 == 0 else inner_radius
            point_x = center_x + int(radius * math.cos(angle))
            point_y = center_y + int(radius * math.sin(angle))
            points.append((point_x, point_y))

        # Draw the main star
        pygame.draw.polygon(screen, color, points, 2)

        # Draw inner decorative circle
        inner_circle_radius = symbol_size // 3
        pygame.draw.circle(screen, color, (center_x, center_y), inner_circle_radius, 1)

        # Draw small decorative dots at each outer point
        dot_radius = size // 16
        for i in range(0, len(points), 2):  # Only outer points
            pygame.draw.circle(screen, color, points[i], dot_radius, 1)

        # Draw central dot
        pygame.draw.circle(screen, color, (center_x, center_y), dot_radius, 1)

    def _draw_spy_symbol(self, screen, x, y, size, owner):
        """Draw spy piece symbol (simple eye shape)"""
        color = BLACK if owner == PLAYER_1 else WHITE
        center_x = int(x + size // 2)
        center_y = int(y + size // 2)
        symbol_size = int(size // 2)

        # Draw main eye shape (single ellipse)
        eye_width = symbol_size
        eye_height = symbol_size // 2
        eye_rect = pygame.Rect(
            center_x - eye_width // 2,
            center_y - eye_height // 2,
            eye_width,
            eye_height
        )
        pygame.draw.ellipse(screen, color, eye_rect, 2)

        # Draw pupil (center dot)
        pygame.draw.circle(screen, color, (center_x, center_y), 2, 0)
