import pygame
from constants import *
from collections import deque


class GameUI:
    def __init__(self, display_manager):
        self.display_manager = display_manager

        # Button dimensions
        self.button_width = 160
        self.button_height = 50
        self.margin = 20

        # Log settings
        self.message_log = deque(maxlen=5)  # Keep last 5 messages
        self.log_font = pygame.font.Font(None, 24)
        self.log_color = (255, 255, 255)  # White text
        self.message_spacing = 25  # Pixels between messages

        # Initialize resign button rect
        self.resign_button_rect = pygame.Rect(
            self.margin,
            self.margin,
            self.button_width,
            self.button_height
        )

        # Initialize menu and rematch button rects
        current_width, current_height = self.display_manager.get_dimensions()

        self.menu_button_rect = pygame.Rect(
            current_width // 2 - 120 - self.button_width // 2,
            current_height // 2 + 70 - self.button_height // 2,
            self.button_width,
            self.button_height
        )

        self.rematch_button_rect = pygame.Rect(
            current_width // 2 + 120 - self.button_width // 2,
            current_height // 2 + 70 - self.button_height // 2,
            self.button_width,
            self.button_height
        )

        # Button states
        self.resign_button_active = False
        self.menu_button_active = False
        self.rematch_button_active = False

    def add_to_log(self, message):
        """Add a message to the log"""
        self.message_log.append(message)

    def draw_log(self, screen):
        """Draw the message log in the bottom left corner"""
        current_width, current_height = self.display_manager.get_dimensions()

        # Start position for the first message
        x = self.margin
        base_y = current_height - (len(self.message_log) * self.message_spacing) - self.margin

        # Draw each message from bottom to top
        for i, message in enumerate(self.message_log):
            # Create text surface with shadow
            shadow_surface = self.log_font.render(message, True, (0, 0, 0))
            text_surface = self.log_font.render(message, True, self.log_color)

            # Position for this message
            y = base_y + (i * self.message_spacing)

            # Draw shadow slightly offset
            screen.blit(shadow_surface, (x + 2, y + 2))
            # Draw text
            screen.blit(text_surface, (x, y))

    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.resign_button_rect.collidepoint(event.pos):
                    return "resign"
                if game_state and self.menu_button_rect.collidepoint(event.pos):
                    return "menu"
                if game_state and self.rematch_button_rect.collidepoint(event.pos):
                    return "rematch"

        elif event.type == pygame.MOUSEMOTION:
            self.resign_button_active = self.resign_button_rect.collidepoint(event.pos)
            if game_state:
                self.menu_button_active = self.menu_button_rect.collidepoint(event.pos)
                self.rematch_button_active = self.rematch_button_rect.collidepoint(event.pos)

        return None

    def get_resign_button_state(self):
        """Return button state for drawing purposes"""
        return {
            'rect': self.resign_button_rect,
            'active': self.resign_button_active
        }

    def get_endgame_button_states(self):
        """Return menu and rematch button states"""
        return {
            'menu': {
                'rect': self.menu_button_rect,
                'active': self.menu_button_active
            },
            'rematch': {
                'rect': self.rematch_button_rect,
                'active': self.rematch_button_active
            }
        }