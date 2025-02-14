from constants import *
import pygame

class DisplayManager:

    def __init__(self, base_width=800, base_height=600, start_fullscreen=False):
        # Base dimensions that game is designed for
        self.base_width = base_width
        self.base_height = base_height

        # Current window state
        self.window_width = base_width
        self.window_height = base_height
        self.is_fullscreen = start_fullscreen

        # Scaling factors
        self.scale_x = 1.0
        self.scale_y = 1.0

        # Set up initial display
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.RESIZABLE
            )

        # Initialize scaling factors
        self._update_scale_factors()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.RESIZABLE
            )
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.is_fullscreen = not self.is_fullscreen
        self._update_scale_factors()

    def handle_resize(self, width, height):
        self.window_width = width
        self.window_height = height
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )
        self._update_scale_factors()

    def _update_scale_factors(self):
        """Update internal scaling factors based on current window size"""
        current_width, current_height = self.screen.get_size()
        self.scale_x = current_width / self.base_width
        self.scale_y = current_height / self.base_height

    # Scaling utility functions
    def scale_pos(self, x, y):
        """Scale a position from base coordinates to current window size"""
        return (x * self.scale_x, y * self.scale_y)

    def scale_size(self, width, height):
        """Scale dimensions from base size to current window size"""
        return (width * self.scale_x, height * self.scale_y)

    def scale_value(self, value):
        """Scale a single value (uses average of x and y scale)"""
        return value * ((self.scale_x + self.scale_y) / 2)

    def get_screen(self):
        """Get the current screen surface"""
        return self.screen

    def get_dimensions(self):
        """Get current screen dimensions"""
        return self.screen.get_size()