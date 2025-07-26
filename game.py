from movement_patterns import get_valid_placement_squares
from draw import MenuDrawUtilities, GameDrawUtilities, DrawUtilities
from sound_manager import SoundManager

from reserve_manager import ReserveManager
from display_manager import DisplayManager
from network_manager import NetworkManager
from game_action_handler import GameActionHandler
from game_ui import GameUI
from pygame import mixer
from board import Board
from constants import *
from menu import Menu
import pygame
import sys


class Game:
    def __init__(self):
        mixer.init()
        pygame.init()
        pygame.display.set_caption("Seiji")
        SoundManager()

        # Game Objects/Managers
        self.clock = pygame.time.Clock()

        print("Creating NetworkManager")
        self.network_manager = NetworkManager(self)

        self.board = Board(BOARD_SIZE, self)
        self.display = DisplayManager(BASE_WINDOW_WIDTH, BASE_WINDOW_HEIGHT, False)
        self.menu = Menu(self, self.display)
        self.game_drawer = GameDrawUtilities(self.display, self.board)
        self.menu_drawer = MenuDrawUtilities(self.display, self.menu)
        self.draw = DrawUtilities(self.display)
        self.reserve_manager = ReserveManager()
        self.screen = self.display.get_screen()
        self.game_ui = GameUI(self.display)

        self.game_action_handler = GameActionHandler(self.board, self.reserve_manager, self.game_ui, self.display)

        # Strings
        self.current_state = "menu"
        self.game_phase = "monarch_placement"
        self.winner = None

        # Piece/Selection Objects
        self.selected_piece = None
        self.selected_reserve_piece = None
        self.current_player = PLAYER_1
        self.current_music = None

        # Lists
        self.valid_moves = []
        self.valid_placement_squares = []

        # Dictionaries
        self.monarchs_placed = {PLAYER_1: False, PLAYER_2: False}

        # Booleans
        self.is_multiplayer = False
        self.display_end_game_screen = False
        self.reserved_piece_selected = False
        self.board_interaction = False

    def handle_input_click(self, pos):

        ui_action = self.game_ui.handle_event(
            type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'pos': pos, 'button': 1})(),
            self.current_state
        )

        if ui_action == "resign":
            SoundManager.play_sound('endgame')
            self.current_state = "post_game"
            self.winner = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1
            return

        board_pos = self.board.get_board_position(pos, self.display)

        player1_reserve_pos = self.reserve_manager.is_click_in_reserve(PLAYER_1, pos, self.display)
        player2_reserve_pos = self.reserve_manager.is_click_in_reserve(PLAYER_2, pos, self.display)

        if board_pos:
            self.handle_board_click(pos)
        elif (self.current_player == PLAYER_1 and player1_reserve_pos) or \
                (self.current_player == PLAYER_2 and player2_reserve_pos):
            self.handle_reserve_click(pos)
        elif not (player1_reserve_pos or player2_reserve_pos):
            self.selected_reserve_piece = None
            self.selected_piece = None
            self.valid_moves = []
            self.valid_placement_squares = []
            SoundManager.play_sound('de_select')

        # Always check piece status after any action
        self.board.check_all_pieces_status()

    def handle_post_game_click(self, pos):
        ui_action = self.game_ui.handle_event(
            type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'pos': pos, 'button': 1})(),
            self.current_state
        )

        if ui_action == "menu":
            SoundManager.play_sound('to_menu')
            self.reset()
            self.draw.fade_to_black(self.screen, 2)
            self.current_state = "menu"

        elif ui_action == "rematch":
            self.current_state = "game"
            self.reset()
            SoundManager.play_sound('rematch')
            SoundManager.handle_music_transition('Sounds/ambient_track.mp3')

    def handle_board_click(self, pos):
        result = self.game_action_handler.handle_board_click(
            pos,
            self.current_player,
            self.game_phase,
            self.selected_piece,
            self.selected_reserve_piece,
            self.valid_moves,
            self.valid_placement_squares,
            self.monarchs_placed,
            self.reserved_piece_selected
        )

        self.selected_piece = result['new_selected_piece']
        self.valid_moves = result['new_valid_moves']
        self.valid_placement_squares = result['new_valid_placement_squares']

        if result['sound_to_play']:
            SoundManager.play_sound(result['sound_to_play'])

        if result['action_taken']:
            if result['log_message']:
                self.game_ui.add_to_log(result['log_message'])

            self.current_player = result['new_player']
            self.monarchs_placed = result['new_monarchs_placed']
            self.game_phase = result['new_game_phase']
            self.reserved_piece_selected = result['reserved_piece_selected']
            self.selected_reserve_piece = result['selected_reserve_piece']

            if result['game_ended']:
                self.winner = result['winner']
                self.current_state = "post_game"
                SoundManager.play_sound('endgame')
                SoundManager.handle_music_transition('Sounds/victory_theme.mp3')

            if result['turn_changed'] or result['action_taken']:
                self.finish_and_send_game_state()

    def handle_reserve_click(self, pos):

        # Retrieve the clicked on reserve piece.
        result = self.game_action_handler.handle_reserve_click(
            pos,
            self.current_player,
            self.selected_reserve_piece,
            self.reserved_piece_selected
        )

        # Ensure that if its te monarch placement phase, we cannot select anything but the monarch.
        new_piece = result['new_selected_reserve_piece']
        if new_piece is not None and new_piece.name != 'monarch' and self.game_phase == 'monarch_placement':

            if self.reserved_piece_selected:
                self.deselect_all()

            SoundManager.play_sound('error')
            return

        self.selected_reserve_piece = result['new_selected_reserve_piece']
        self.reserved_piece_selected = result['new_reserved_piece_selected']
        self.valid_moves = result['new_valid_moves']
        self.valid_placement_squares = result['new_valid_placement_squares']

        if result['sound_to_play']:
            SoundManager.play_sound(result['sound_to_play'])

    def deselect_all(self):
        self.selected_piece = None
        self.valid_moves = []
        self.valid_placement_squares = []
        self.selected_reserve_piece = None
        self.reserved_piece_selected = False
        SoundManager.play_sound('de_select')

    def finish_and_send_game_state(self):
        if self.is_multiplayer:
            self.board.check_all_pieces_status()
            self.network_manager.send_game_state()

    def reset(self):
        self.monarchs_placed = {PLAYER_1: False, PLAYER_2: False}
        self.game_phase = "monarch_placement"
        self.current_state = "game"

        self.board.wipe_board()
        self.reserve_manager.reset_reserves()

        self.current_player = PLAYER_1

        self.winner = None
        self.selected_piece = None
        self.selected_reserve_piece = None
        self.reserved_piece_selected = False

        self.valid_moves = []
        self.valid_placement_squares = []

    def handle_states(self):
        if self.current_state == "menu":
            SoundManager.handle_music_transition('Sounds/menu_theme.mp3')
            self.menu_drawer.draw(self.screen)
            return

        if self.current_state == "game":
            SoundManager.handle_music_transition('Sounds/ambient_track.mp3')
            self.network_manager.process_network_updates()
            self.board.check_all_pieces_status()

        self.game_drawer.draw(self.screen, self.valid_placement_squares, self.valid_moves, self.game_phase)
        self.game_drawer.draw_reserve_pieces(self.screen, self.reserve_manager, self.selected_reserve_piece)
        self.game_ui.draw_log(self.screen)

        if self.current_state == "post_game":
            self.game_drawer.draw_game_over_screen(self.screen, self.winner)

    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.menu_drawer.handle_resize()
                self.game_drawer.handle_resize()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

            if self.current_state == "menu":
                self.menu.handle_event(event)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_state == "game":
                    self.handle_input_click(event.pos)
                    continue

                if self.current_state == "post_game":
                    self.handle_post_game_click(event.pos)

    def run(self):
        while True:
            self.handle_states()
            self.handle_events()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()