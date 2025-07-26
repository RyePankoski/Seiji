import pygame
import threading
from draw import DrawUtilities
from server import GameServer
from sound_manager import SoundManager


class Menu:
    def __init__(self, game, display_manager):
        SoundManager()

        self.confirm_button_rect = None
        self.setup_dialog_rect = None
        self.buttons = None
        self.button_borders = None
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

        self.show_rules = False  # Add this line
        self.rules_image = pygame.image.load("Images/Rules.png")
        self.rules_scroll_y = 0  # Add scroll position
        self.rules_scroll_speed = 30

        self.show_settings = False
        self.settings_font = pygame.font.Font("Fonts/general_text.ttf", 36)

        # Volume settings (0.0 to 1.0)
        self.music_volume = 0.3
        self.sound_volume = 0.7

        # Slider dimensions
        self.slider_width = 300
        self.slider_height = 20
        self.slider_handle_width = 20

        # Dragging state
        self.dragging_music = False
        self.dragging_sound = False

    def create_buttons(self):
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
            "How To Play",
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
        if event.type == pygame.VIDEORESIZE:
            self.create_buttons()
            return

        if event.type == pygame.KEYDOWN:
            if self.show_setup_dialog:
                self.handle_setup_input(event)
            elif self.show_ip_dialog:
                self.handle_ip_input(event)
            return

        # Handle scrolling when rules are open
        if event.type == pygame.MOUSEWHEEL and self.show_rules:
            self.rules_scroll_y -= event.y * self.rules_scroll_speed
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_setup_dialog:
                self._handle_setup_dialog_click(event.pos)
            elif self.show_ip_dialog:
                self.show_ip_dialog = False
            elif self.show_rules:
                self.show_rules = False
                self.rules_scroll_y = 0
            elif self.show_settings:
                self._handle_settings_click(event.pos)
            else:
                self.handle_menu_click(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.show_settings:
                self.dragging_music = False
                self.dragging_sound = False
            return

        if event.type == pygame.MOUSEMOTION and self.show_settings:
            self._handle_settings_drag(event.pos)
            return

    def _handle_setup_dialog_click(self, pos):
        if self.confirm_button_rect.collidepoint(pos):
            try:
                board_size = int(self.board_size_input)
                if 4 <= board_size <= 16:
                    self.game.board.resize_board(board_size)
                    self.show_setup_dialog = False
                    self.setup_confirmed = True
                    self.draw.fade_to_black(self.display_manager.get_screen())
                    self.game.current_state = "game"
                    SoundManager.choose_random_ambience(force=True)
            except ValueError:
                self.board_size_input = "9"
        elif not self.setup_dialog_rect.collidepoint(pos):
            self.show_setup_dialog = False

    def handle_setup_input(self, event):
        if event.key == pygame.K_RETURN:
            try:
                board_size = int(self.board_size_input)
                if 4 <= board_size <= 19:
                    self.game.board.resize_board(board_size)
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
                    SoundManager.play_sound('play')
                    self.show_setup_dialog = True
                elif text == "Join Game":
                    SoundManager.play_sound('join_game')
                    self.show_ip_dialog = True
                elif text == "How To Play":
                    SoundManager.play_sound('how_to_play')
                    self.show_rules = not self.show_rules
                elif text == "Settings":
                    SoundManager.play_sound('settings')
                    self.show_settings = not self.show_settings  # Add this
                elif text == "Exit":
                    pygame.quit()
                    exit()
                elif text == "Host Game":
                    SoundManager.play_sound('host_game')
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

    def _handle_settings_click(self, pos):
        current_width, current_height = self.display_manager.get_dimensions()

        # Settings dialog dimensions
        dialog_width = 500
        dialog_height = 400
        dialog_x = (current_width - dialog_width) // 2
        dialog_y = (current_height - dialog_height) // 2

        # Check if clicking outside settings dialog
        settings_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        if not settings_rect.collidepoint(pos):
            self.show_settings = False
            return

        # Music slider
        music_slider_x = dialog_x + 50
        music_slider_y = dialog_y + 120
        music_slider_rect = pygame.Rect(music_slider_x, music_slider_y, self.slider_width, self.slider_height)

        if music_slider_rect.collidepoint(pos):
            self.dragging_music = True
            # Set volume based on click position
            relative_x = pos[0] - music_slider_x
            self.music_volume = max(0.0, min(1.0, relative_x / self.slider_width))
            SoundManager.set_music_volume(self.music_volume)

        # Sound slider
        sound_slider_x = dialog_x + 50
        sound_slider_y = dialog_y + 220
        sound_slider_rect = pygame.Rect(sound_slider_x, sound_slider_y, self.slider_width, self.slider_height)

        if sound_slider_rect.collidepoint(pos):
            self.dragging_sound = True
            relative_x = pos[0] - sound_slider_x
            self.sound_volume = max(0.0, min(1.0, relative_x / self.slider_width))
            SoundManager.set_sound_volume(self.sound_volume)

    def _handle_settings_drag(self, pos):
        """Handle dragging sliders"""
        current_width, current_height = self.display_manager.get_dimensions()

        dialog_width = 500
        dialog_height = 400
        dialog_x = (current_width - dialog_width) // 2
        dialog_y = (current_height - dialog_height) // 2

        if self.dragging_music:
            music_slider_x = dialog_x + 50
            relative_x = pos[0] - music_slider_x
            self.music_volume = max(0.0, min(1.0, relative_x / self.slider_width))
            SoundManager.set_music_volume(self.music_volume)

        if self.dragging_sound:
            sound_slider_x = dialog_x + 50
            relative_x = pos[0] - sound_slider_x
            self.sound_volume = max(0.0, min(1.0, relative_x / self.slider_width))
            SoundManager.set_sound_volume(self.sound_volume)

