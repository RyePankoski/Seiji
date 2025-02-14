import pygame
import threading
from draw import DrawUtilities
from server import GameServer
from network_manager import NetworkManager


class Menu:
    def __init__(self, game, display_manager):
        self.display_manager = display_manager
        self.game = game
        self.show_ip_dialog = False
        self.show_setup_dialog = False
        self.ip_input = ""
        self.board_size_input = "9"  # Default board size
        self.selected_button = None
        self.create_buttons()
        self.server = None
        self.server_thread = None
        self.draw = DrawUtilities(self.display_manager)
        self.setup_confirmed = False

    def create_buttons(self):
        """Create menu buttons with their positions and text"""
        current_width, current_height = self.display_manager.get_dimensions()

        # Button dimensions
        button_width = 300
        button_height = 80
        button_spacing = 20

        # Calculate starting Y position for first button
        start_y = current_height // 2 - (button_height * 2 + button_spacing * 1.5)

        # Create buttons list with (rect, text) tuples and their borders
        self.buttons = []
        self.button_borders = []

        button_data = [
            "Play Local",
            "Join Game",
            "Host Game",
            "Settings",
            "Exit"
        ]

        for i, text in enumerate(button_data):
            button_y = start_y + (button_height + button_spacing) * i

            # Create button rectangle
            button_rect = pygame.Rect(
                (current_width - button_width) // 2,
                button_y,
                button_width,
                button_height
            )

            # Create border rectangle (slightly larger)
            border_rect = button_rect.inflate(4, 4)

            self.buttons.append((button_rect, text))
            self.button_borders.append(border_rect)

        # Create setup dialog buttons
        dialog_width = 400
        dialog_height = 300
        self.setup_dialog_rect = pygame.Rect(
            (current_width - dialog_width) // 2,
            (current_height - dialog_height) // 2,
            dialog_width,
            dialog_height
        )

        # Create confirm button for setup dialog
        confirm_width = 120
        confirm_height = 40
        self.confirm_button_rect = pygame.Rect(
            self.setup_dialog_rect.centerx - confirm_width // 2,
            self.setup_dialog_rect.bottom - 60,
            confirm_width,
            confirm_height
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_setup_dialog:
                if self.confirm_button_rect.collidepoint(event.pos):
                    try:
                        board_size = int(self.board_size_input)
                        if 4 <= board_size <= 16:  # Validate board size
                            self.game.board.size = board_size
                            self.show_setup_dialog = False
                            self.setup_confirmed = True
                            self.draw.fade_to_black(self.display_manager.get_screen())
                            self.game.current_state = "game"
                    except ValueError:
                        self.board_size_input = "9"  # Reset to default if invalid
                elif not self.setup_dialog_rect.collidepoint(event.pos):
                    self.show_setup_dialog = False
            elif self.show_ip_dialog:
                self.show_ip_dialog = False
            else:
                self.handle_menu_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if self.show_setup_dialog:
                self.handle_setup_input(event)
            elif self.show_ip_dialog:
                self.handle_ip_input(event)

        elif event.type == pygame.VIDEORESIZE:
            self.create_buttons()

    def handle_setup_input(self, event):
        if event.key == pygame.K_RETURN:
            try:
                board_size = int(self.board_size_input)
                if 4 <= board_size <= 19:
                    self.game.board.size = board_size
                    self.show_setup_dialog = False
                    self.setup_confirmed = True
                    self.draw.fade_to_black(self.display_manager.get_screen())
                    self.game.current_state = "game"
            except ValueError:
                self.board_size_input = "9"
        elif event.key == pygame.K_BACKSPACE:
            self.board_size_input = self.board_size_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.show_setup_dialog = False
        elif event.unicode in "0123456789" and len(self.board_size_input) < 2:
            self.board_size_input += event.unicode

    def handle_menu_click(self, pos):
        for i, (button_rect, text) in enumerate(self.buttons):
            if button_rect.collidepoint(pos):
                if text == "Play Local":
                    self.show_setup_dialog = True
                elif text == "Join Game":
                    self.show_ip_dialog = True
                elif text == "Exit":
                    pygame.quit()
                    exit()
                elif text == "Host Game":
                    if not hasattr(self, 'server') or self.server is None:
                        self.server = GameServer()
                        self.server_thread = threading.Thread(target=self.server.start)
                        self.server_thread.daemon = True
                        self.server_thread.start()

                self.selected_button = i
                break

    def handle_ip_input(self, event):
        if event.key == pygame.K_RETURN:
            self.game.network_manager.connect_to_server(self.ip_input, 5555)
            self.game.is_multiplayer = True
            self.game.current_state = "game"
            self.show_ip_dialog = False
        elif event.key == pygame.K_BACKSPACE:
            self.ip_input = self.ip_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.show_ip_dialog = False
        elif event.unicode in "0123456789.":
            self.ip_input += event.unicode

