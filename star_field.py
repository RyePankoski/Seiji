import random
import pygame
from constants import *

class StarPoint:
    def __init__(self, center_x, center_y, star_color, min_speed=0.1, max_size=10, growth_rate=150):
        # Create spawn area
        offset_x = random.uniform(-20, 20)
        offset_y = random.uniform(-20, 20)
        self.position = [center_x + offset_x, center_y + offset_y]
        self.center = (center_x, center_y)
        self.size = 0.5
        self.max_size = max_size
        self.growth_rate = growth_rate

        # Initialize vector with minimum speed constraint
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)

        # Normalize the vector to ensure consistent speed
        length = (x * x + y * y) ** 0.5
        if length > 0:
            x = x / length
            y = y / length

        # Apply minimum speed
        if x > 0:
            x = max(min_speed, x)
        else:
            x = min(-min_speed, x)

        if y > 0:
            y = max(min_speed, y)
        else:
            y = min(-min_speed, y)

        self.vector = (x, y)
        self.color = star_color

    def update(self, speed):
        # Update position based on vector
        self.position[0] += self.vector[0] * speed
        self.position[1] += self.vector[1] * speed

        # Calculate distance from center
        dx = self.position[0] - self.center[0]
        dy = self.position[1] - self.center[1]
        distance = (dx * dx + dy * dy) ** 0.5

        # Gradually increase size based on distance
        self.size = 0.5 + (distance / self.growth_rate)
        self.size = min(self.max_size, self.size)

    def update_center(self, new_center_x, new_center_y):
        """Update the star's position and center when window is resized"""
        dx = self.position[0] - self.center[0]
        dy = self.position[1] - self.center[1]
        self.center = (new_center_x, new_center_y)
        self.position[0] = new_center_x + dx
        self.position[1] = new_center_y + dy

    def is_off_screen(self, width, height):
        """Check if star is off screen with a much larger margin"""
        margin = max(width, height) * 0.5  # Use half the screen size as margin
        return (self.position[0] < -margin or
                self.position[0] > width + margin or
                self.position[1] < -margin or
                self.position[1] > height + margin)


class MenuStarfield:
    def __init__(self, width, height, config=None):
        self.width = width
        self.height = height

        # Default configuration
        default_config = {
            'max_stars': 200,
            'speed': 5,
            'spawn_interval': 2,
            'min_star_speed': 0.1,
            'max_star_size': 10,
            'growth_rate': 150,
            'colored_star_chance': 2,
            'background_color': (10, 10, 20),
            'default_star_color': (255, 255, 255)
        }

        # Update defaults with provided config
        self.config = default_config
        if config:
            self.config.update(config)

        self.stars = []
        self.center = (width // 2, height // 2)
        self.frame_counter = 0

    def update(self):
        self.frame_counter += 1

        # Handle star spawning
        if (self.frame_counter % self.config['spawn_interval'] == 0 and
                len(self.stars) < self.config['max_stars']):

            star_chance = random.uniform(0, 100)
            if star_chance > 100 - self.config['colored_star_chance']:
                star_color = (random.uniform(0, 255),
                              random.uniform(0, 255),
                              random.uniform(0, 255))
            else:
                star_color = self.config['default_star_color']

            self.stars.append(StarPoint(
                self.center[0],
                self.center[1],
                star_color,
                self.config['min_star_speed'],
                self.config['max_star_size'],
                self.config['growth_rate']
            ))

        # Update existing stars and remove off-screen ones
        self.stars = [star for star in self.stars if not star.is_off_screen(self.width, self.height)]
        for star in self.stars:
            star.update(self.config['speed'])

    def draw(self, screen):
        if self.config.get('fill_background', True):
            screen.fill(self.config['background_color'])

        for star in self.stars:
            pygame.draw.circle(screen, star.color,
                               (int(star.position[0]), int(star.position[1])),
                               star.size)

    def resize(self):
        width, height = self.display_manager.get_dimensions()
        new_center = (width // 2, height // 2)

        for star in self.stars:
            star.update_center(new_center[0], new_center[1])

        self.center = new_center