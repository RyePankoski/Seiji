from movement_patterns import get_valid_moves, get_valid_placement_squares
from draw import MenuDrawUtilities, GameDrawUtilities, DrawUtilities
from reserve_manager import ReserveManager
from display_manager import DisplayManager
from network_manager import NetworkManager
from game_ui import GameUI
from pygame import mixer
from board import Board
from constants import *
from menu import Menu
import pygame
import sys


class Game:
    def __init__(self):
        # Initialize Pygame and Audio
        mixer.init()
        pygame.init()
        pygame.display.set_caption("Seiji")

        # Sound Objects
        self.place_sound = pygame.mixer.Sound("Sounds/place_sound.mp3")
        self.slide_sound = pygame.mixer.Sound("Sounds/slide_sound.mp3")
        self.pick_up_sound = pygame.mixer.Sound("Sounds/pick_up.mp3")
        self.capture_sound = pygame.mixer.Sound("Sounds/capture.mp3")
        self.promote_sound = pygame.mixer.Sound("Sounds/promote.mp3")
        self.endgame_sound = pygame.mixer.Sound("Sounds/endgame.mp3")
        self.select_piece_sound = pygame.mixer.Sound("Sounds/advisor.mp3")
        self.de_select_sound = pygame.mixer.Sound("Sounds/de-select.mp3")
        self.enemy_select_sound = pygame.mixer.Sound("Sounds/enemy_select.mp3")

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
        def _handle_reserve_placement(board_pos, center):
            try:
                if self.selected_reserve_piece is None:
                    return

                if self.selected_reserve_piece.owner != self.current_player:
                    return

                if self.game_phase == "monarch_placement":
                    if not self.selected_reserve_piece.name == "monarch":
                        return
                    if board_pos[0] == center and board_pos[1] == center:
                        return
                    if board_pos not in self.valid_placement_squares and self.valid_placement_squares is not None:
                        return

                if board_pos not in self.valid_placement_squares and self.valid_placement_squares is not None:
                    self.selected_reserve_piece = None
                    self.deselect()
                    return

                if self.board.place_piece(self.selected_reserve_piece, board_pos):
                    x, y = board_pos

                    self.game_ui.add_to_log(f"Player {self.current_player} placed a {self.selected_reserve_piece.name} "
                                            f"at {x + 1, BOARD_SIZE - y}")

                    player = self.selected_reserve_piece.owner
                    piece_index = self.reserve_manager.get_pieces(player).index(self.selected_reserve_piece)
                    self.reserve_manager.remove_piece(player, piece_index)
                    self.place_sound.play()

                    if self.selected_reserve_piece.name == "monarch":
                        self.monarchs_placed[player] = True
                        if all(self.monarchs_placed.values()):
                            self.game_phase = "playing"

                    self.selected_piece = None
                    self.valid_moves = []
                    self.valid_placement_squares = []
                    self.current_player = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1
                    self.finish_and_send_game_state()
            finally:
                self.reserved_piece_selected = False

        def _handle_board_interaction(board_pos, clicked_piece_inside):
            if self.valid_moves is None:
                self.valid_moves = []  # Ensure it's always a list

            if self.selected_piece:
                if board_pos in self.valid_moves and self.selected_piece.owner == self.current_player:
                    _move_piece(board_pos, clicked_piece_inside)
                else:
                    _select_piece(clicked_piece_inside, board_pos)
            elif clicked_piece_inside:
                _select_piece(clicked_piece_inside, board_pos)

        def _move_piece(board_pos, clicked_piece_inside):
            old_pos = next(((x, y) for y, row in enumerate(self.board.board)
                            for x, piece in enumerate(row) if piece == self.selected_piece), None)
            x, y = board_pos

            if clicked_piece_inside and clicked_piece_inside.owner != self.selected_piece.owner:
                self.board.remove_piece(old_pos)
                self.board.remove_piece(board_pos)
                captured_piece = clicked_piece_inside
                captured_piece.owner = self.current_player  # Change the owner to the capturing player
                # Finally place the capturing piece
                self.board.place_piece(self.selected_piece, board_pos)
                self.capture_sound.play()

                self.game_ui.add_to_log(f"Player {self.current_player} captured {self.selected_piece.name} at "
                                        f"{x + 1, BOARD_SIZE - y}")

                if clicked_piece_inside.name == "monarch":
                    self.endgame_sound.play()
                    self.current_state = "post_game"

                    if self.current_player == PLAYER_1:
                        self.winner = PLAYER_2
                    else:
                        self.winner = PLAYER_1
                    self.finish_and_send_game_state()
                else:
                    self.reserve_manager.add_piece(captured_piece)
                    self.finish_and_send_game_state()
            else:
                self.board.remove_piece(old_pos)
                self.board.place_piece(self.selected_piece, board_pos)

                self.game_ui.add_to_log(f"Player {self.current_player} moved {self.selected_piece.name} to "
                                        f"{x + 1, BOARD_SIZE - y}")

                self.slide_sound.play()
                self.finish_and_send_game_state()

            self.deselect()
            self.selected_piece = None
            self.valid_moves = []
            self.current_player = PLAYER_2 if self.current_player == PLAYER_1 else PLAYER_1

        def _select_piece(clicked_piece_inside, board_pos):
            if not clicked_piece_inside:
                self.selected_piece = None
                self.valid_moves = []
                self.de_select_sound.play()
                return

            if self.selected_piece == clicked_piece_inside:
                self.valid_moves = []
                self.selected_piece = None
                return

            self.selected_piece = clicked_piece_inside
            self.valid_moves = get_valid_moves(clicked_piece_inside, board_pos[0], board_pos[1], self.board)

            if clicked_piece_inside.owner == self.current_player:
                self.select_piece_sound.play()
            else:
                self.enemy_select_sound.play()

        top_board_pos = self.board.get_board_position(pos, self.display)
        top_center = self.board.size // 2

        if self.reserved_piece_selected:
            _handle_reserve_placement(top_board_pos, top_center)
        else:
            clicked_piece = self.board.get_piece(top_board_pos)
            _handle_board_interaction(top_board_pos, clicked_piece)

    def deselect(self):
        """Handle piece deselection and cleanup"""
        self.selected_piece = None
        self.valid_moves = []
        self.valid_placement_squares = []
        self.de_select_sound.play()

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
            self.pick_up_sound.play()
            self.selected_reserve_piece = piece
            self.reserved_piece_selected = True
            self.valid_placement_squares = get_valid_placement_squares(self.board, piece)
        else:
            self.reserved_piece_selected = False
            self.selected_reserve_piece = None

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
                        self.endgame_sound.play()
                        self.current_state = "post_game"

                        if self.current_player == PLAYER_1:
                            winner = PLAYER_2
                        else:
                            winner = PLAYER_1

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
        self.monarchs_placed = False
        self.monarchs_placed = {PLAYER_1: False, PLAYER_2: False}
        self.board.wipe_board()
        self.reserve_manager.reset_reserves()
        self.current_player = PLAYER_1

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
            #hello



if __name__ == "__main__":
    game = Game()
    game.run()
