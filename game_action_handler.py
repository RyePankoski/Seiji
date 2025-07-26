from movement_patterns import get_valid_moves
from sound_manager import SoundManager
from constants import *


class GameActionHandler:
    def __init__(self, board, reserve_manager, game_ui, display):
        self.board = board
        self.reserve_manager = reserve_manager
        self.game_ui = game_ui
        self.display = display

    def handle_board_click(self, pos, current_player, game_phase, selected_piece,
                           selected_reserve_piece, valid_moves, valid_placement_squares,
                           monarchs_placed, reserved_piece_selected):

        result = {
            'action_taken': False,
            'game_ended': False,
            'winner': None,
            'turn_changed': False,
            'new_player': current_player,
            'new_selected_piece': selected_piece,
            'new_valid_moves': valid_moves,
            'new_valid_placement_squares': valid_placement_squares,
            'new_monarchs_placed': monarchs_placed,
            'new_game_phase': game_phase,
            'reserved_piece_selected': reserved_piece_selected,
            'selected_reserve_piece': selected_reserve_piece,
            'sound_to_play': None,
            'log_message': None
        }

        def _handle_reserve_placement(board_pos, center):

            if selected_reserve_piece is None:
                return

            if selected_reserve_piece.owner != current_player:
                return

            if game_phase == "monarch_placement":
                if not selected_reserve_piece.name == "monarch":
                    return
                if board_pos[0] == center and board_pos[1] == center:
                    return
                if board_pos not in valid_placement_squares and valid_placement_squares is not None:
                    return

            if board_pos not in valid_placement_squares and valid_placement_squares is not None:
                result['selected_reserve_piece'] = None
                result['sound_to_play'] = 'de_select'
                return

            if self.board.place_piece(selected_reserve_piece, board_pos):
                x, y = board_pos
                result[
                    'log_message'] = (f"Player {current_player} placed a {selected_reserve_piece.name} at "
                                      f"{x + 1, self.board.size - y}")

                player = selected_reserve_piece.owner
                piece_index = self.reserve_manager.get_pieces(player).index(selected_reserve_piece)
                self.reserve_manager.remove_piece(player, piece_index)
                result['sound_to_play'] = 'place'

                if selected_reserve_piece.name == "monarch":
                    new_monarchs = monarchs_placed.copy()
                    new_monarchs[player] = True
                    result['new_monarchs_placed'] = new_monarchs
                    if all(new_monarchs.values()):
                        result['new_game_phase'] = "playing"

                result['new_selected_piece'] = None
                result['new_valid_moves'] = []
                result['new_valid_placement_squares'] = []
                result['new_player'] = PLAYER_2 if current_player == PLAYER_1 else PLAYER_1
                result['turn_changed'] = True
                result['action_taken'] = True
                result['reserved_piece_selected'] = False

        def _handle_board_interaction(board_pos, clicked_piece_inside):
            safe_valid_moves = valid_moves if valid_moves is not None else []

            if selected_piece:
                if board_pos in safe_valid_moves and selected_piece.owner == current_player:
                    _move_piece(board_pos, clicked_piece_inside)
                else:
                    _select_piece(clicked_piece_inside, board_pos)
            elif clicked_piece_inside:
                _select_piece(clicked_piece_inside, board_pos)

        def _move_piece(board_pos, clicked_piece_inside):
            old_pos = next(((x, y) for y, row in enumerate(self.board.board)
                            for x, piece in enumerate(row) if piece == selected_piece), None)
            x, y = board_pos

            if clicked_piece_inside and clicked_piece_inside.owner != selected_piece.owner:
                # Capture move
                self.board.remove_piece(old_pos)
                self.board.remove_piece(board_pos)
                captured_piece = clicked_piece_inside
                captured_piece.owner = current_player
                self.board.place_piece(selected_piece, board_pos)

                result['sound_to_play'] = 'capture'
                result[
                    'log_message'] = f"Player {current_player} captured {selected_piece.name} at {x + 1, BOARD_SIZE - y}"

                if clicked_piece_inside.name == "monarch":
                    result['sound_to_play'] = 'endgame'
                    result['game_ended'] = True
                    result['winner'] = PLAYER_1 if current_player == PLAYER_2 else PLAYER_2
                else:
                    self.reserve_manager.add_piece(captured_piece)
            else:
                # Normal move
                self.board.remove_piece(old_pos)
                self.board.place_piece(selected_piece, board_pos)
                result[
                    'log_message'] = f"Player {current_player} moved {selected_piece.name} to {x + 1, BOARD_SIZE - y}"
                result['sound_to_play'] = 'slide'

            result['new_selected_piece'] = None
            result['new_valid_moves'] = []
            result['new_player'] = PLAYER_2 if current_player == PLAYER_1 else PLAYER_1
            result['turn_changed'] = True
            result['action_taken'] = True

        def _select_piece(clicked_piece_inside, board_pos):
            if not clicked_piece_inside:
                result['new_selected_piece'] = None
                result['new_valid_moves'] = []
                result['sound_to_play'] = 'de_select'
                result['action_taken'] = True
                return

            if selected_piece == clicked_piece_inside:
                result['new_valid_moves'] = []
                result['new_selected_piece'] = None
                result['action_taken'] = True
                return

            result['new_selected_piece'] = clicked_piece_inside
            result['new_valid_moves'] = get_valid_moves(clicked_piece_inside, board_pos[0], board_pos[1], self.board)
            result['action_taken'] = True

            if clicked_piece_inside.owner == current_player:
                result['sound_to_play'] = 'select_piece'
            else:
                result['sound_to_play'] = 'enemy_select'

        # Main logic
        top_board_pos = self.board.get_board_position(pos, self.display)
        top_center = self.board.size // 2

        if reserved_piece_selected:
            _handle_reserve_placement(top_board_pos, top_center)
        else:
            clicked_piece = self.board.get_piece(top_board_pos)
            _handle_board_interaction(top_board_pos, clicked_piece)

        return result
