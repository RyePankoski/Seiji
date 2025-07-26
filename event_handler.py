import sys

import pygame
from constants import *
from sound_manager import SoundManager


class EventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.game.menu_drawer.handle_resize()
                self.game.game_drawer.handle_resize()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

            if self.game.current_state == "menu":
                self.game.menu.handle_event(event)
                continue

            if self.game.current_state == "game":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    ui_action = self.game.game_ui.handle_event(event, self.game.current_state)

                    if ui_action == "resign":
                        SoundManager.play_sound('endgame')
                        self.game.current_state = "post_game"
                        self.game.winner = PLAYER_2 if self.game.current_player == PLAYER_1 else PLAYER_1
                        continue

                    # Handle game clicks
                    board_pos = self.game.board.get_board_position(event.pos, self.game.display)
                    reserve_pos = self.game.reserve_manager.is_click_in_reserve(self.game.current_player, event.pos,
                                                                                self.game.display)

                    if board_pos:
                        self.game.handle_board_click(event.pos)
                    elif reserve_pos:
                        self.game.handle_reserve_click(event.pos)
                    else:
                        self.game.selected_reserve_piece = None
                        self.game.deselect()

                    self.game.board.check_all_pieces_status()

                continue

            if self.game.current_state == "post_game":
                ui_action = self.game.game_ui.handle_event(event, self.game.current_state)

                if ui_action == "menu":
                    SoundManager.play_sound('to_menu')
                    self.game.handle_reset()
                    self.game.draw.fade_to_black(self.game.screen, 2)
                    self.game.current_state = "menu"
                elif ui_action == "rematch":
                    SoundManager.play_sound('rematch')
                    self.game.current_state = "game"
                    self.game.handle_reset()
