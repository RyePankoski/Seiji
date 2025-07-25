from movement_patterns import get_valid_placement_squares
from draw import MenuDrawUtilities, GameDrawUtilities, DrawUtilities
from sound_manager import SoundManager
from reserve_manager import ReserveManager
from display_manager import DisplayManager
from network_manager import NetworkManager
from board_handler import BoardHandler
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

        # NEW: Board handler for decoupled board logic
        self.board_handler = BoardHandler(self.board, self.reserve_manager, self.game_ui, self.display)

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

    def handle_music_transition(self, new_track, fadeout_time=1000):
        if new_track == self.current_music:  # Skip if same track
            return
        try:
            mixer.music.fadeout(fadeout_time)
            mixer.music.load(new_track)
            mixer.music.play(-1)
            self.current_music = new_track
        except pygame.error as e:
            print(f"Could not load or play music file: {e}")

    def handle_board_click(self, pos):
        result = self.board_handler.handle_board_click(
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

        # ALWAYS update selection state, regardless of action_taken
        self.selected_piece = result['new_selected_piece']
        self.valid_moves = result['new_valid_moves']
        self.valid_placement_squares = result['new_valid_placement_squares']

        # Play sounds if specified (even for just selections)
        if result['sound_to_play']:
            SoundManager.play_sound(result['sound_to_play'])

        # Only update other state if a major action occurred
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
                self.handle_music_transition('Sounds/victory_theme.mp3')

            if result['turn_changed'] or result['action_taken']:
                self.finish_and_send_game_state()

    def handle_reserve_click(self, pos):
        self.valid_moves = []
        self.valid_placement_squares = []
        dimensions = self.display.get_dimensions()
        current_width, current_height = dimensions
        click_x, click_y = pos

        piece = self.reserve_manager.get_piece_at_position(
            self.current_player,
            click_x,
            click_y,
            current_width,
            current_height
        )

        if self.reserved_piece_selected is True and piece == self.selected_reserve_piece:
            self.deselect()
            self.selected_reserve_piece = None
            return

        if piece is not None:
            SoundManager.play_sound('pick_up')
            self.selected_reserve_piece = piece
            self.reserved_piece_selected = True
            self.valid_placement_squares = get_valid_placement_squares(self.board, piece)
        else:
            self.reserved_piece_selected = False
            self.selected_reserve_piece = None

    def deselect(self):
        self.selected_piece = None
        self.valid_moves = []
        self.valid_placement_squares = []
        SoundManager.play_sound('de_select')



    def finish_and_send_game_state(self):
        if self.is_multiplayer:
            self.board.check_all_pieces_status()
            self.network_manager.send_game_state()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                self.menu_drawer.handle_resize()
                self.game_drawer.handle_resize()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            if self.current_state == "menu":
                self.menu.handle_event(event)
                continue

            if self.current_state == "game":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    ui_action = self.game_ui.handle_event(event, self.current_state)
                    board_pos = self.board.get_board_position(event.pos, self.display)
                    reserve_pos = self.reserve_manager.is_click_in_reserve(self.current_player, event.pos, self.display)

                    if ui_action == "resign":
                        SoundManager.play_sound('endgame')
                        self.current_state = "post_game"
                        self.winner = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1
                        self.handle_music_transition('Sounds/victory_theme.mp3')
                        return

                    if board_pos:
                        self.handle_board_click(event.pos)
                    elif reserve_pos:
                        self.handle_reserve_click(event.pos)
                    else:
                        self.selected_reserve_piece = None
                        self.deselect()

                    self.board.check_all_pieces_status()

            if self.current_state == "post_game":
                ui_action = self.game_ui.handle_event(event, self.current_state)
                if ui_action == "menu":
                    self.handle_reset()
                    self.draw.fade_to_black(self.screen, 2)
                    self.current_state = "menu"
                    return
                if ui_action == "rematch":
                    self.current_state = "game"
                    self.handle_reset()

    def handle_reset(self):
        self.monarchs_placed = {PLAYER_1: False, PLAYER_2: False}
        self.board.wipe_board()
        self.reserve_manager.reset_reserves()
        self.current_player = PLAYER_1
        self.selected_piece = None
        self.selected_reserve_piece = None
        self.valid_moves = []
        self.valid_placement_squares = []
        self.reserved_piece_selected = False
        self.winner = None

        self.current_state = "game"
        self.game_phase = "monarch_placement"

    def handle_states(self):
        if self.current_state == "menu":
            self.handle_music_transition('Sounds/menu_theme.mp3')
            self.menu_drawer.draw(self.screen)
        elif self.current_state == "game":
            self.network_manager.process_network_updates()
            self.board.check_all_pieces_status()
            self.game_drawer.draw(self.screen, self.valid_placement_squares, self.valid_moves, self.game_phase)
            self.game_drawer.draw_reserve_pieces(self.screen, self.reserve_manager, self.selected_reserve_piece)
            self.handle_music_transition('Sounds/ambient_track.mp3')
            self.game_ui.draw_log(self.screen)

        elif self.current_state == "post_game":
            self.game_drawer.draw(self.screen, self.valid_placement_squares, self.valid_moves, self.game_phase)
            self.game_drawer.draw_reserve_pieces(self.screen, self.reserve_manager, self.selected_reserve_piece)
            self.game_drawer.draw_game_over_screen(self.screen, self.winner)
            self.game_ui.draw_log(self.screen)

    def run(self):
        while True:
            self.handle_events()
            self.handle_states()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()