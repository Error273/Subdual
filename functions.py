import pygame
import sys
import random
import os

import math
from constants import *
import game_classes


def get_distance(obj1, obj2):
    # возвращает расстояние между центрами двух спрайтов
    return math.sqrt((obj1.rect.centerx - obj2.rect.centerx) ** 2 + (obj1.rect.centery - obj2.rect.centery) ** 2)


def calculate_night_saturation_coef(daytime):
    # Функция, описывающая зависимость коэффициента затемнения от времени суток
    saturation_coef = 0
    if daytime <= 33:
        saturation_coef = 3 * daytime
    elif 33 < daytime <= 66:
        saturation_coef = 100
    elif daytime < 100:
        saturation_coef = -3 * daytime + 298
    saturation_coef *= 0.7
    return saturation_coef


def spawn_object(ObjectClass, *args, min_x, min_y, max_x, max_y, collide_group):
    # спавнит объект на случайном месте таким образом, чтобы он не входил в другой объект

    # сперва берем первую случайную позицию и список объектов, с которыми он столкнулся
    obj = ObjectClass(random.randint(min_x, max_x),
                      random.randint(min_y, max_y),
                      *args)
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
                          *args)
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
def load_image(name):
    fullname = os.path.join('Images', name)
    image = pygame.image.load(fullname)
    return image


# Функция для создания волны врагов
def spawn_enemies(day_number, buildings_group, enemies_group, *init_groups, grid):
    # шанс спавна волны в конкретный кадр. может повести и враги в какой то день не придут.
    # с увеличением дня повышается и шанс
    chance = day_number
    # количество врагов, которое надо заспавнить
    enemies = day_number * COMPLICATION_COEF
    if random.randint(0, 1000) < chance:
        for _ in range(int(enemies)):
            # ограничиваем количество противников в целях оптимизации
            if len(enemies_group) < MAX_ENEMIES_AMOUNT:
                spawn_object(random.choice([game_classes.TacticalCamel, game_classes.Camel]), buildings_group,
                             *init_groups,
                             min_x=grid.rect.x, min_y=grid.rect.y,
                             max_x=grid.width * CELL_SIZE,
                             max_y=grid.height * CELL_SIZE,
                             collide_group=buildings_group)
            else:
                return True
        return True
    return False
