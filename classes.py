import pygame
from constants import *


class Grid:
    # серая сетка на фоне, по которой будут выравниваться постройки.
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self, surface, camera_x, camera_y):
        # вместо целых квадратов рисуем линиями, так как быстрее нарисовать 200 линий, чем 10 000 квадратов
        for i in range(self.width + 1):
            pygame.draw.line(surface, 'grey', (camera_x + i * CELL_SIZE, camera_y),
                             (camera_x + i * CELL_SIZE, camera_y + self.height * CELL_SIZE))

        for i in range(self.height + 1):
            pygame.draw.line(surface, 'grey', (camera_x, camera_y + i * CELL_SIZE),
                             (camera_x + self.width * CELL_SIZE, camera_y + i * CELL_SIZE))


class Player:
    # главный игрок
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.going_left = False
        self.going_right = False
        self.going_up = False
        self.going_down = False
        self.is_building = False

    def update(self):
        if self.going_up:
            self.y -= PLAYER_MOVEMENT_SPEED
        if self.going_left:
            self.x -= PLAYER_MOVEMENT_SPEED
        if self.going_right:
            self.x += PLAYER_MOVEMENT_SPEED
        if self.going_down:
            self.y += PLAYER_MOVEMENT_SPEED

    def draw(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, 'black', (camera_x + self.x,
                                            camera_y + self.y,
                                            CELL_SIZE,
                                            CELL_SIZE * 2))

    def set_going_up(self, going_up):
        self.going_up = going_up

    def set_going_down(self, going_down):
        self.going_down = going_down

    def set_going_left(self, going_left):
        self.going_left = going_left

    def set_going_right(self, going_right):
        self.going_right = going_right

    def set_is_building(self, is_building):
        self.is_building = is_building

    def get_is_building(self):
        return self.is_building


class BaseBuilding:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        pass

    def draw(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, (227, 208, 64), (camera_x + self.x, camera_y + self.y, self.width, self.height))
