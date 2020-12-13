import pygame
from constants import *


class Grid:
    # серая сетка на фоне, по которой будут выравниваться постройки.
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self, surface, camera_x, camera_y):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(surface, 'grey', (camera_x + j * CELL_SIZE,
                                                   camera_y + i * CELL_SIZE,
                                                   CELL_SIZE,
                                                   CELL_SIZE), 1)


class Player:
    # главный игрок
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.going_left = False
        self.going_right = False
        self.going_up = False
        self.going_down = False

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
