from functions import *


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
    def __init__(self, x, y, sound_channel, *groups):
        super().__init__(*groups)

        # картинки для движения по всем направлениям. пришлось задавать их вручную, так как анимация похода влево-вправо
        # отличается по длине, а так же важен порядок их добавления
        self.animations = [[load_image(os.path.join('PlayerAnimations', 'down', i)) for i in ['1.png', 'static.png',
                                                                                              '2.png', 'static.png']],
                           [load_image(os.path.join('PlayerAnimations', 'left', i)) for i in ['1.png', '2.png',
                                                                                              '3.png']],

                           [load_image(os.path.join('PlayerAnimations', 'up', i)) for i in ['1.png', 'static.png',
                                                                                            '2.png', 'static.png']],

                           [load_image(os.path.join('PlayerAnimations', 'right', i)) for i in ['1.png', '2.png',
                                                                                               '3.png']]]

        # картинки для стояния
        self.static_images = [pygame.image.load(os.path.join('Images', 'PlayerAnimations', i, 'static.png'))
                              for i in ['down', 'left', 'up', 'right']]

        # на каком кадре анимации мы сейчас находимся. 3 - это покой
        self.animation_counter = 0
        # в какую сторону мы идем. 0 - вниз, ...,  3 - вправо
        self.rotation_position = 0

        # текущий кадр
        self.image = self.static_images[self.rotation_position]

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

        # Была ли поставлена главная постройка. Проверяется для принятия решение о блокировке постройки
        # и изменении слота постройки
        self.were_placed_main_building = False
        self.were_destroyed_main_building = False

        # инвентарь игрока. удобно держать его в виде словаря
        self.inventory = {'stones': 0,
                          'wood': 0}

        # тики игрока, необходимы для внутренних таймеров
        self.ticks = 0

        self.sound_channel = sound_channel

        self.walking_sounds = [pygame.mixer.Sound(os.path.join('Sounds', 'Player', 'walking', f'{i}.mp3'))
                               for i in range(1, 3)]
        [sound.set_volume(0.1) for sound in self.walking_sounds]

        # Выбранная постройка
        self.selected_building = 0

    def update(self, grid, builings_group):
        self.ticks += 1

        # сперва двигаем игрока куда он хочет
        if self.going_up:
            # поворачиваем спрайт игрока
            self.rotation_position = 2
            # изменяем позицию
            self.rect.y -= PLAYER_MOVEMENT_SPEED
        if self.going_left:
            self.rotation_position = 1
            self.rect.x -= PLAYER_MOVEMENT_SPEED
        if self.going_right:
            self.rotation_position = 3
            self.rect.x += PLAYER_MOVEMENT_SPEED
        if self.going_down:
            self.rotation_position = 0
            self.rect.y += PLAYER_MOVEMENT_SPEED

        # если мы сейчас двигаемся, то меняем кадр анимации и переопределяем изображение
        if any([self.going_up, self.going_down, self.going_left, self.going_right]):

            if not self.sound_channel.get_busy():
                self.sound_channel.play(random.choice(self.walking_sounds))

            if self.ticks % PLAYER_MOVEMENT_SPEED == 0:
                # следующий новый кадр анимации
                self.animation_counter = (self.animation_counter + 1) % len(self.animations[self.rotation_position])
                # меняем кадр
                self.image = self.animations[self.rotation_position][self.animation_counter]
        # если мы остановили движение, то выбираем статичный кадр
        else:
            self.image = self.static_images[self.rotation_position]
            self.sound_channel.stop()

        # проверяем, не столкнулся ли он с чем нибудь. если да, двигаем его назад
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
    # Отличается от BaseBuilding только тем, что у нее есть тип PlayerBuilding и звуковой канал
    # у каждой постройки должен быть свой тип для того, чтобы игрок не мог полностью разрушать постройки,
    # сделанные не им
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)

        self.building_type = 'PlayerBuilding'
        self.health = 200

        self.sound_channel = None

    def get_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.play_destroying_sound()
            self.kill()

    def set_sound_channel(self, sound_channel):
        self.sound_channel = sound_channel

    def play_building_sound(self):
        pass

    def play_destroying_sound(self):
        pass


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

        self.health = WOODEN_FENCE_HEALTH

        # звуки для постройки
        self.building_sounds = [pygame.mixer.Sound(os.path.join('Sounds', 'WoodenFence', 'building',
                                                                f'{i}.mp3')) for i in range(1, 4)]
        # звуки для уничтожения
        self.destroying_sound = pygame.mixer.Sound(os.path.join('Sounds', 'WoodenFence', 'destroying', '1.mp3'))

    def play_building_sound(self):
        if self.sound_channel:
            self.sound_channel.play(random.choice(self.building_sounds))

    def play_destroying_sound(self):
        if self.sound_channel:
            self.sound_channel.play(self.destroying_sound)


class DoubleBarrelTurret(PlayerBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)
        # прогружаем все картинки с анимациями
        # представляем из себя двухмерный массив, где первая строка - это анимации стрельбы вниз, вторая влево,
        # третья вверх, четвертая вниз
        self.images = [[load_image(os.path.join('DoubleBarrelTurretAnimations', j, i))
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
        self.focused_target = None

        # ставим картинку
        self.image = self.images[self.rotation_position][self.animation_counter]
        self.rect = self.image.get_rect().move(x, y)

        self.health = DOUBLE_BARREL_TURRET_HEALTH

        self.ticks = 0

        # звуки стрельбы
        self.shooting_sounds = [pygame.mixer.Sound(os.path.join('Sounds', 'DoubleBarrelTurret', 'shooting', '1.wav')),
                                pygame.mixer.Sound(os.path.join('Sounds', 'DoubleBarrelTurret', 'shooting', '2.ogg'))]
        [sound.set_volume(0.5) for sound in self.shooting_sounds]

        # Звуки при постройке
        self.building_sounds = [pygame.mixer.Sound(os.path.join('Sounds', 'DoubleBarrelTurret', 'building',
                                                                f'{i}.mp3')) for i in range(1, 4)]

        # звуки при уничтожении
        self.destroying_sound = pygame.mixer.Sound(os.path.join('Sounds', 'DoubleBarrelTurret', 'destroying', '1.flac'))

    def update(self, targets_group):
        self.ticks += 1

        # если у нас нет цели, то ищем одну.
        if not self.focused_target:
            for target in targets_group:
                # смотрим, достаем ли мы до цели
                if get_distance(self, target) <= DOUBLE_BARREL_TURRET_SHOOTING_RADIUS:
                    self.focused_target = target
                    break
        # а если у нас есть цель, но она уже мертва, то сбрасываем цель
        elif self.focused_target.health <= 0:
            self.focused_target = None

        # если попали в тайминг смены кадра
        if self.ticks % DOUBLE_BARREL_TURRET_SHOOTING_SPEED == 0:
            # меняем кадр анимации и переопределяем изображение
            self.animation_counter = (self.animation_counter + 1) % len(self.images[self.animation_counter])
            self.image = self.images[self.rotation_position][self.animation_counter]

            # если сейчас не стреляем, устанавливаем кадр покоя
            if not self.focused_target:
                self.image = self.images[self.rotation_position][1]
            else:
                # наносим урон, если находимся на кадре стрельбы
                if self.animation_counter in [0, 2]:
                    self.focused_target.get_damage(DOUBLE_BARREL_TURRET_DAMAGE)
                    self.play_shooting_sound()
                # если стреляем, то смотрим, в какой стороне от турели находится цель, и туда разворачиваемся
                if self.focused_target.rect.right < self.rect.left:
                    self.rotation_position = 1
                elif self.focused_target.rect.left > self.rect.right:
                    self.rotation_position = 3
                elif self.focused_target.rect.bottom > self.rect.top:
                    self.rotation_position = 0
                elif self.focused_target.rect.top < self.rect.bottom:
                    self.rotation_position = 2

    def play_building_sound(self):
        if self.sound_channel:
            self.sound_channel.play(random.choice(self.building_sounds))

    def play_destroying_sound(self):
        if self.sound_channel:
            self.sound_channel.play(self.destroying_sound)

    def play_shooting_sound(self):
        if self.sound_channel:
            self.sound_channel.play(random.choice(self.shooting_sounds))


class MainBuilding(PlayerBuilding):
    def __init__(self, x, y, *groups):
        super().__init__(x, y, *groups)

        self.images = [pygame.image.load('Images/MainBuilding/' + str(i) + '.png') for i in range(1, 4)]
        self.image = self.images[0]
        self.rect = self.image.get_rect().move(x, y)

        self.health = MAIN_BUILDING_HEALTH

        # переменные, отвечающие за анимацию
        self.tics = pygame.time.get_ticks()
        self.indexes = (0, 1, 2, 1, 0)
        self.i = 0

        self.building_sound = pygame.mixer.Sound(os.path.join('Sounds', 'MainBuilding', 'building', '1.mp3'))
        self.destroying_sound = pygame.mixer.Sound(os.path.join('Sounds', 'MainBuilding', 'destroying', '1.mp3'))

    def update(self, player):
        # Картинка меняется каждые 1000 тиков
        if pygame.time.get_ticks() - self.tics > 1000:
            self.image = self.images[self.indexes[self.i]]
            self.tics = pygame.time.get_ticks()
            self.i += 1
        if self.i == 4:
            self.i = 0

    def get_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            restart_game()
            self.play_destroying_sound()
            self.kill()

    def play_building_sound(self):
        if self.sound_channel:
            self.sound_channel.play(self.building_sound)

    def play_destroying_sound(self):
        if self.sound_channel:
            self.sound_channel.play(self.destroying_sound)


class Enemy(pygame.sprite.Sprite):  # базовый класс противника. без картинки, без анимаций, ии ближней атаки
    def __init__(self, x, y, buildings_group, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((100, 100))

        self.rect = self.image.get_rect().move(x, y)
        # главное здание, к которому будем идти.
        self.main_building = None
        self.health = 100

        self.ticks = 0

        self.sound_channel = None

        # ищем среди всех построек главное здание и сохраняем себе
        for building in buildings_group:
            if type(building) == MainBuilding:
                self.main_building = building
                break

    def update(self, buildings_group):
        self.ticks += 1

        # вычисляем вектор смещения персонажа
        deltax, deltay = self.move(1)
        # двигаемся
        self.rect.centerx += deltax
        self.rect.centery += deltay

        # смотрим, во что мы врезались
        collide_building = pygame.sprite.spritecollideany(self, buildings_group)
        if collide_building:
            # если врезались в дерево/камень, то пытаемся его обойти
            # может работать коряво, но это лучшая попытка.
            if collide_building.building_type == 'GeneratedBuilding':
                if self.rect.right > collide_building.rect.left or self.rect.left < collide_building.rect.right:
                    self.rect.y -= TACTICAL_CAMEL_MOVING_SPEED
                if self.rect.top < collide_building.rect.bottom or self.rect.bottom > collide_building.rect.top:
                    self.rect.x += TACTICAL_CAMEL_MOVING_SPEED
            # если врезались, то возвращаемся обратно
            self.rect.top -= deltay
            self.rect.right -= deltax

    def move(self, speed):  # функция вычислящая вектор смещения себя к цели
        # если главное здание существует, то смещаемся. во всех других случаях нет
        if self.main_building:
            # получаем координаты центров себя и цели
            x1, y1 = self.rect.centerx, self.rect.centery
            x2, y2 = self.main_building.rect.centerx, self.main_building.rect.centery
            # вычисляем вектор, в направлении которого нужно двигаться
            deltax = x2 - x1
            deltay = y2 - y1
            # получаем длину этого вектора, и проверяем его, чтобы не поделить на 0
            vector_len = math.sqrt(deltax ** 2 + deltay ** 2)
            if vector_len != 0:
                # нормализируем вектор, чтобы мы всегда двигались с одинаковой скоростью и можно было эту скорость
                # настраивать
                deltax = round(deltax / vector_len * speed)
                deltay = round(deltay / vector_len * speed)

                return deltax, deltay
        return 0, 0

    def get_damage(self, damage):  # получить урон. если нет здоровья, умираем
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def set_sound_channel(self, sound_channel):
        self.sound_channel = sound_channel


class Camel(Enemy):  # обычный боец ближнего боя.
    def __init__(self, x, y, buildings_group, *groups):
        super().__init__(x, y, buildings_group, *groups)

        # анимации походки
        self.images = [[load_image(os.path.join('CamelAnimations', rotation, i))
                        for i in ['1.png', '2.png', '1.png', '3.png']] for rotation in ['left', 'right']]

        self.rotation_position = 0  # куда повернут объект. 0 - влево, 1 - вправо
        self.animation_counter = 0  # на каком шаге анимации сейчас находимся
        self.animation_speed = 15  # скорость смены кадра

        # текущий кадр
        self.image = self.images[self.rotation_position][self.animation_counter]

        self.rect = self.image.get_rect().move(x, y)

        self.health = CAMEL_HEALTH

    def update(self, buildings_group):
        # делаем то же самое что и в родительском классе, но добавляем анимацию и наносим урон постройке игрока,
        # если столкнулись

        self.ticks += 1

        # двигаемся
        deltax, deltay = self.move(CAMEL_MOVING_SPEED)
        self.rect.centerx += deltax
        self.rect.centery += deltay

        # меняем кадр при движении
        if self.ticks % (self.animation_speed - CAMEL_MOVING_SPEED) == 0:
            self.animation_counter = (self.animation_counter + 1) % len(self.images[self.rotation_position])
            if deltax < 0:
                self.rotation_position = 0
            else:
                self.rotation_position = 1

            self.image = self.images[self.rotation_position][self.animation_counter]

        # Проверяем столкновения. если столкнулись с постройкой игрока, наносим ей урон
        collide_building = pygame.sprite.spritecollideany(self, buildings_group)
        if collide_building:
            if collide_building.building_type == 'GeneratedBuilding':
                if self.rect.right > collide_building.rect.left or self.rect.left < collide_building.rect.right:
                    self.rect.y -= CAMEL_MOVING_SPEED
                if self.rect.top < collide_building.rect.bottom or self.rect.bottom > collide_building.rect.top:
                    self.rect.x += CAMEL_MOVING_SPEED
            else:
                if self.ticks % CAMEL_ATTACK_SPEED == 0:
                    collide_building.get_damage(CAMEL_DAMAGE)

            # отменяем последнее движение
            self.rect.top -= deltay
            self.rect.right -= deltax


class TacticalCamel(Enemy):  # боец, который атакует с растояния
    def __init__(self, x, y, buildings_group, *groups):
        super().__init__(x, y, buildings_group, *groups)

        # анимации ходьбы
        self.images = [[load_image(os.path.join('TacticalCamelAnimations', i, j))
                        for j in ['1.png', '2.png', '1.png', '3.png']] for i in ['left', 'right']]

        # анимации атаки
        self.attacking_images = [load_image(os.path.join('TacticalCamelAnimations', 'shooting', 'left.png')),
                                 load_image(os.path.join('TacticalCamelAnimations', 'shooting', 'right.png'))]

        self.rotation_position = 0
        self.animation_counter = 0
        self.animation_speed = 15

        self.image = self.images[self.rotation_position][self.animation_counter]
        self.rect = self.image.get_rect().move(x, y)

        self.health = TACTICAL_CAMEL_HEALTH

        self.shooting_sounds = [pygame.mixer.Sound(os.path.join('Sounds', 'TacticalCamel', 'shooting', f'{i}.wav'))
                                for i in range(1, 4)]

    def update(self, buildings_group):
        self.ticks += 1

        # проверяем, находимся ли мы рядом с какой то постройкой игрока.
        # если да, то пропускаем продолжение функции, так как далше идет обработка движения
        for building in buildings_group:
            if get_distance(self, building) <= TACTICAL_CAMEL_ATTACK_RADIUS:
                if building.building_type == 'PlayerBuilding':
                    # делим выстрел на 2 части. первая - кадр стрельбы, во время которого наносим урон.
                    # второй - кадр перезарядки, устанавливаем статитчную картинку
                    if self.ticks % (TACTICAL_CAMEL_ATTACK_SPEED // 2) == 0:
                        if self.image == self.attacking_images[self.rotation_position]:
                            self.image = self.images[self.rotation_position][0]
                        else:
                            self.image = self.attacking_images[self.rotation_position]
                            building.get_damage(TACTICAL_CAMEL_DAMAGE)
                            self.play_shooting_sound()
                    return

        deltax, deltay = self.move(TACTICAL_CAMEL_MOVING_SPEED)

        if self.ticks % (self.animation_speed - TACTICAL_CAMEL_MOVING_SPEED) == 0:
            self.animation_counter = (self.animation_counter + 1) % len(self.images[self.rotation_position])
            if deltax < 0:
                self.rotation_position = 0
            else:
                self.rotation_position = 1

            self.image = self.images[self.rotation_position][self.animation_counter]

        self.rect.centerx += deltax
        self.rect.centery += deltay

        collide_building = pygame.sprite.spritecollideany(self, buildings_group)
        if collide_building:
            if collide_building.building_type == 'GeneratedBuilding':
                if self.rect.right > collide_building.rect.left or self.rect.left < collide_building.rect.right:
                    self.rect.y -= CAMEL_MOVING_SPEED
                if self.rect.top < collide_building.rect.bottom or self.rect.bottom > collide_building.rect.top:
                    self.rect.x += CAMEL_MOVING_SPEED

            self.rect.top -= deltay
            self.rect.right -= deltax

    def play_shooting_sound(self):
        if self.sound_channel:
            self.sound_channel.play(random.choice(self.shooting_sounds))
