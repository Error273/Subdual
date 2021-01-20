import os

from functions import *
from random import randint


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WINDOW_WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - WINDOW_HEIGHT // 2)


class Grid(pygame.sprite.Sprite):
    # серая сетка на фоне, по которой будут выравниваться постройки.
    # представляет из себя прозрачный surface, на котором рисуются непрозрачные линии
    def __init__(self, width, height, *groups):
        super().__init__(*groups)
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width * CELL_SIZE + 1, self.height * CELL_SIZE + 1), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()

        for i in range(self.width + 1):
            pygame.draw.line(self.image, 'grey', (i * CELL_SIZE, 0),
                             (i * CELL_SIZE, self.height * CELL_SIZE))

        for i in range(self.height + 1):
            pygame.draw.line(self.image, 'grey', (0, i * CELL_SIZE),
                             (self.width * CELL_SIZE, i * CELL_SIZE))

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class Player(pygame.sprite.Sprite):
    # главный игрок
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(os.path.join('Images', 'Гелик(стоит).png'))
        self.rect = self.image.get_rect().move(x, y)

        # игроку нужно знать позицию мыши для того, чтобы при добыче дерева/камня игрок всегда держал мышь на объекте.
        # так как функция, проверяющая может ли игрок добывать находится в классе, то и позиция мыши тоже должна быть
        # в классе
        self.mouse_pos = (0, 0)

        self.going_left = False
        self.going_right = False
        self.going_up = False
        self.going_down = False

        # класс постройки, которую мы предположительно строим. здесь что-то оказыватся только при нажатии клавиш,
        # отвечающих за включение режима строительства какого-то объекта
        self.potential_building = None

        # объект, который мы сейчас добываем. его необходимо держать в классе для того,
        # чтобы измерять до него расстояние
        self.mining_instance = None

        # инвентарь игрока. удобно держать его в виде словаря
        self.inventory = {'stones': 0,
                          'wood': 0}

        # тики игрока, необходимы для внутренних таймеров
        self.ticks = 0

    def update(self, grid, builings_group):
        self.ticks += 1

        # сперва двигаем игрока куда он хочет
        if self.going_up:
            self.rect.y -= PLAYER_MOVEMENT_SPEED
        if self.going_left:
            self.rect.x -= PLAYER_MOVEMENT_SPEED
        if self.going_right:
            self.rect.x += PLAYER_MOVEMENT_SPEED
        if self.going_down:
            self.rect.y += PLAYER_MOVEMENT_SPEED
        # а потом проверяем, не столкнулся ли он с чем нибудь. если да, двигаем его назад
        self.check_collisions(grid, builings_group)

        # перед тем, как зачислить игроку ресурс, нужно проверить, можно ли его добывать
        self.check_can_mine()
        # если у нас есть ресурс для добычи и мы попали в тайминг для добычи
        if self.mining_instance:
            if self.mining_instance.type == 'Tree' and self.ticks % MINING_SPEED == 0:
                self.inventory['wood'] += 1
            elif self.mining_instance.type == 'Rock' and self.ticks % MINING_SPEED == 0:
                self.inventory['stones'] += 1

    def check_collisions(self, grid, buildings_group):
        # Условия для ограничения выхода за пределы поля
        if self.rect.top < grid.rect.top and self.going_up:
            self.set_going_up(False)
            self.rect.top += PLAYER_MOVEMENT_SPEED
        if self.rect.left < grid.rect.left and self.going_left:
            self.set_going_left(False)
            self.rect.left += PLAYER_MOVEMENT_SPEED
        if self.rect.right > grid.rect.right and self.going_right:
            self.set_going_right(False)
            self.rect.right -= PLAYER_MOVEMENT_SPEED
        if self.rect.bottom > grid.rect.bottom and self.going_down:
            self.set_going_down(False)
            self.rect.bottom -= PLAYER_MOVEMENT_SPEED

        # Проверка на столкновения с постройками
        # FIXME: неприятно управлять игроком, при врезании во что то он как будто прилипает
        # берем все спрайты, с которыми столкнулся игрок
        for building in pygame.sprite.spritecollide(self, buildings_group, False):
            # проверяем, зашел ли игрок в спрайт. если да, останавливаем его движение и двигаем обратно
            # смотрим для каждой стороны
            if self.rect.bottom > building.rect.top and self.going_down:
                self.set_going_down(False)
                self.rect.bottom -= PLAYER_MOVEMENT_SPEED

            if self.rect.top < building.rect.bottom and self.going_up:
                self.set_going_up(False)
                self.rect.top += PLAYER_MOVEMENT_SPEED

            if self.rect.right > building.rect.left and self.going_right:
                self.set_going_right(False)
                self.rect.right -= PLAYER_MOVEMENT_SPEED

            if self.rect.left < building.rect.right and self.going_left:
                self.set_going_left(False)
                self.rect.left += PLAYER_MOVEMENT_SPEED

    def check_can_mine(self):
        # на добычу есть 2 основных ограничения: чтобы игрок находился достаточно близко и мышь была на ресурсе
        # если они не выполняются, то просто убираем ресурс из возможности добычи
        if self.mining_instance and not (get_distance(self, self.mining_instance) <= MINING_DISTANCE and
                                         self.mining_instance.rect.collidepoint(*self.mouse_pos)):
            self.mining_instance = None

    def set_going_up(self, going_up):
        self.going_up = going_up

    def set_going_down(self, going_down):
        self.going_down = going_down

    def set_going_left(self, going_left):
        self.going_left = going_left

    def set_going_right(self, going_right):
        self.going_right = going_right

    def set_potential_building(self, potential_building):
        self.potential_building = potential_building

    def get_potential_building(self):
        return self.potential_building

    def set_mining_instance(self, mining_instance):
        self.mining_instance = mining_instance

    def set_mouse_pos(self, pos):
        self.mouse_pos = pos

    def get_mouse_pos(self):
        return self.mouse_pos


class BaseBuilding(pygame.sprite.Sprite):
    # базовый класс того, что стоит на земле и не двигается
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x, y)


class PlayerBuilding(BaseBuilding):
    # базовый класс построки, сделанной игроком.
    # Отличается от BaseBuilding только тем, что у нее есть тип PlayerBuilding
    # у каждой постройки должен быть свой тип для того, чтобы игрок не мог полностью разрушать постройки,
    # сделанные не им
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.building_type = 'PlayerBuilding'


class GeneratedBuilding(BaseBuilding):
    # построки, сгенерированные автоматически
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.building_type = 'GeneratedBuilding'


class Tree(GeneratedBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.images = ['tree_tall.png', 'tree_wide.png']
        # выбираем случайное дерево из возможных
        self.image = pygame.image.load(os.path.join('Images', random.choice(self.images)))
        self.rect = self.image.get_rect().move(x, y)
        self.type = 'Tree'


class Rock(GeneratedBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.images = ['rock.png', 'rock_small.png']
        self.image = pygame.image.load(os.path.join('Images', random.choice(self.images)))
        self.rect = self.image.get_rect().move(x, y)
        self.type = 'Rock'


class WoodenFence(PlayerBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        self.image = pygame.image.load(os.path.join('Images', 'Стена 1.png'))
        self.rect = self.image.get_rect().move(x, y)


class DoubleBarrelTurret(PlayerBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        # прогружаем все картинки с анимациями
        # представляем из себя двухмерный массив, где первая строка - это анимации стрельбы вниз, вторая влево,
        # третья вверх, четвертая вниз
        self.images = [[pygame.image.load(os.path.join('Images', 'DoubleBarrelTurretAnimations', j, i))
                        for i in ['double_barrel_turret_shoot_left.png',
                                  'double_barrel_turret.png',
                                  'double_barrel_turret_shoot_right.png',
                                  'double_barrel_turret.png']] for j in ('down', 'left', 'up', 'right')
                       ]
        # на каком кадре анимации мы сейчас находимся. 3 - это покой
        self.animation_counter = 3
        # в какую сторону направлена турель. 0 - вниз, ...,  3 - вправо
        self.rotation_position = 0

        # стреляет ли сейчас турель
        self.shooting = False

        # ставим картинку
        self.image = self.images[self.rotation_position][self.animation_counter]
        self.rect = self.image.get_rect().move(x, y)

        self.ticks = 0

        # минимальный радиус до цели, с которого можно стрелять
        self.shooting_radius = 200

        # с какой скоростью ведется стрельба
        self.shooting_speed = 15

    def update(self, target):
        self.ticks += 1

        # смотрим, достаем ли мы до цели. для тестирования стреляем в игрока
        if get_distance(self, target) <= self.shooting_radius:
            self.shooting = True
        else:
            self.shooting = False
        # если попали в тайминг смены кадра
        if self.ticks % self.shooting_speed == 0:
            # меняем кадр анимации и переопределяем изображение
            self.animation_counter = (self.animation_counter + 1) % len(self.images[self.animation_counter])
            self.image = self.images[self.rotation_position][self.animation_counter]

            # если сейчас не стреляем, устанавливаем кадр покоя
            if not self.shooting:
                self.image = self.images[self.rotation_position][1]
            else:
                # если стреляем, то смотрим, в какой стороне от турели находится цель, и туда разворачиваемся
                if target.rect.right < self.rect.left:
                    self.rotation_position = 1
                elif target.rect.left > self.rect.right:
                    self.rotation_position = 3
                elif target.rect.bottom > self.rect.top:
                    self.rotation_position = 0
                elif target.rect.top < self.rect.bottom:
                    self.rotation_position = 2