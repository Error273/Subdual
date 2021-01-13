import pygame
import sys
import random
import os

from math import sqrt
from constants import *


def get_distance(obj1, obj2):
    # возвращает расстояние между центрами двух спрайтов
    return sqrt((obj1.rect.centerx - obj2.rect.centerx) ** 2 + (obj1.rect.centery - obj2.rect.centery) ** 2)


def spawn_object(ObjectClass, max_x, max_y, collide_group, *init_groups):
    # спавнит объект на случайном месте таким образом, чтобы он не входил в другой объект

    # сперва берем первую случайную позицию и список объектов, с которыми он столкнулся
    obj = ObjectClass(random.randint(0, max_x),
                      random.randint(0, max_y),
                      *init_groups)
    collided = pygame.sprite.spritecollide(obj, collide_group, False)

    # если объект находится в той же группе, что и группа спрайтов для столкновения, то его столкновение самого
    # с собой стоит игнорировать
    if obj in collided:
        collided.remove(obj)

    while collided:
        # если объект в чем-то находится, то мы его удаляем и повторяем шаги
        obj.kill()
        obj = ObjectClass(random.randint(0, max_x),
                          random.randint(0, max_y),
                          *init_groups)
        collided = pygame.sprite.spritecollide(obj, collide_group, False)
        if obj in collided:
            collided.remove(obj)

    return obj


def terminate():
    # выходит из программы
    pygame.quit()
    sys.exit()


def align_building(x, y, grid):
    # отравнивает потенциальную постройку по сетке с учетом курсора
    return x - x % CELL_SIZE + grid.rect.x % CELL_SIZE, y - y % CELL_SIZE + grid.rect.y % CELL_SIZE


# Функция для загрузки изображения
def load_image(name, color_key=None):
    print(name)
    fullname = os.path.join('Images', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image
