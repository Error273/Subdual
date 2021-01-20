from game_classes import *
from hud_classes import *

pygame.init()
screen = pygame.display.set_mode(SIZE)

running = True
clock = pygame.time.Clock()
tics = 0
daytime = 0
day_number = 1

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()

hud = Hud()
buildings_preset_drawer = DrawBuildingsPresets()

# "тень" здания, которое мы собираемся построить
building_shadow = None

grid = Grid(100, 100, all_sprites)

# инициализация серфейсов
gui_surface = pygame.Surface(SIZE, pygame.SRCALPHA, 32)
day_night_surface = pygame.Surface(SIZE, pygame.SRCALPHA, 32)
buildings_choice_surface = pygame.Surface((2 * 100, 120), pygame.SRCALPHA, 32)

# генерируем камни
for _ in range(ROCKS_AMOUNT):
    # вычитаем 75 и 75, так как мы не хотим, чтобы камень выходило за границы поля
    rock = spawn_object(Rock, grid.width * CELL_SIZE - 75, grid.height * CELL_SIZE - 75, buildings_group,
                        buildings_group, all_sprites)

# генерируем деревья
for _ in range(TREES_AMOUNT):
    # вычитаем 50 и 75, так как мы не хотим, чтобы дерево выходило за границы поля
    tree = spawn_object(Tree, grid.width * CELL_SIZE - 50, grid.height * CELL_SIZE - 75, buildings_group,
                        buildings_group, all_sprites)

player = spawn_object(Player, grid.width * CELL_SIZE - 25, grid.height * CELL_SIZE - 50, buildings_group, all_sprites,
                      player_group)

camera = Camera()

while running:
    # выводим фпс в название окна
    pygame.display.set_caption(str(clock.get_fps()))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # если нажали на крестик, выходим
            running = False
            terminate()
            continue

        # если мы нажали на кнопку мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # если сейчас можно строить
            if player.get_potential_building():
                if event.button == 1:  # если нажали на левую кнопку

                    # привязываем постройку к сетке
                    x, y = align_building(x, y, grid)

                    # проверяем, не выходит ли постройка за карту
                    if grid.rect.top <= y <= grid.rect.bottom - building_shadow.get_height() and \
                            grid.rect.left <= x <= grid.rect.right - building_shadow.get_width():

                        building = player.get_potential_building()(x, y, buildings_group, all_sprites)
                        # проверяем, сколько объектов находится на месте постройки. пропускаем 2 потому, что это сетка и
                        # сама постройка
                        if len(pygame.sprite.spritecollide(building, all_sprites, False)) > 2:
                            # удаляем построку совсем
                            building.kill()

                elif event.button == 3:  # если нажали на правую кнопку мыши, то построку стоит удалить
                    for building in buildings_group:
                        if building.rect.collidepoint(x, y) and building.building_type == 'PlayerBuilding':
                            building.kill()

            if event.button == 1:
                # смотрим, на какую постройку мы нажали. вносим игроку данные о добываемом объекте.
                for building in buildings_group:
                    # начинаем добычу только если добываем дерево/камень и если сейчас не строим
                    if building.rect.collidepoint(x, y) and building.building_type == 'GeneratedBuilding' and \
                            not player.get_potential_building():
                        player.set_mining_instance(building)
                        # в этой функции проверяем, можно ли добывать этот объект
                        player.check_can_mine()

        # если отпустили мышку, то прекращаем всю добычу
        if event.type == pygame.MOUSEBUTTONUP:
            player.set_mining_instance(None)

        # игроку нужно знать где находится мышка для того, чтобы знать, находится ли она на добываемом объекте
        if event.type == pygame.MOUSEMOTION:
            player.set_mouse_pos(event.pos)
        if event.type == pygame.KEYDOWN:
            # если нажата клавиша вниз, то начинаем движение
            if event.key == pygame.K_w and player.rect.y >= 0:
                player.set_going_up(True)
            if event.key == pygame.K_a and player.rect.x >= 0:
                player.set_going_left(True)
            if event.key == pygame.K_s and player.rect.y < grid.height * CELL_SIZE:
                player.set_going_down(True)
            if event.key == pygame.K_d and player.rect.x < grid.width * CELL_SIZE:
                player.set_going_right(True)

            # если нажали на кнопку, отмеченную для строительства
            if event.key in range(pygame.K_1, pygame.K_2 + 1):
                buildings_preset_drawer.selected_building = event.key - 48
                if player.get_potential_building(): # если режим строительства уже включен, то его нужно выключить
                    buildings_preset_drawer.selected_building = 0
                    player.set_potential_building(None)
                else:
                    # выбираем забор
                    if event.key == pygame.K_1:
                        player.set_potential_building(WoodenFence)
                    # выбираем турель
                    elif event.key == pygame.K_2:
                        player.set_potential_building(DoubleBarrelTurret)
                    # устанавливаем тень выбранной постройки перед строительством
                    building_shadow = player.get_potential_building()(0, 0).image
                    # увеличиваем прозрачность
                    building_shadow.set_alpha(128)

        if event.type == pygame.KEYUP:
            # если клавиша отпущена, движение прекращаем
            if event.key == pygame.K_w:
                player.set_going_up(False)
            if event.key == pygame.K_a:
                player.set_going_left(False)
            if event.key == pygame.K_s:
                player.set_going_down(False)
            if event.key == pygame.K_d:
                player.set_going_right(False)

    screen.fill(BACKGROUND_COLOR)

    # FIXME: при движении игрок сам сдвигается в сторону движения, то есть его координаты на экране меняются (а они не
    # должны, так как камерой мы фокусим игрока)
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    # показываем сетку только если сейчас можно строить
    # показываем наполовину прозрачное изображение выбранной постройки с координатами курсора мыши
    if player.get_potential_building():
        grid.draw(screen)
        # нам нет необходимости заного получать и хранить координаты мыши в главном файле, так как они уже хранятся
        # в Player'e
        screen.blit(building_shadow, align_building(*player.get_mouse_pos(), grid))

    # отрисовываем все постройки
    buildings_group.update(player) # пока в качестве цели для турели возьмем игрока
    buildings_group.draw(screen)

    # Обновляем и отрисовывем игрока
    player_group.update(grid, buildings_group)
    player_group.draw(screen)

    # Функция, описывающая зависимость коэффициента затемнения от времени суток
    if daytime <= 33:
        x = 3 * daytime
    elif 33 < daytime <= 66:
        x = 100
    elif daytime < 100:
        x = -3 * daytime + 298

    # Затемнение поля
    pygame.draw.rect(day_night_surface, pygame.Color(15, 32, 161, int(x * 0.7)), (0, 0, SIZE[0], SIZE[1]), 0)

    # Расчеты, связанные с циклом дня и ночи
    tics = pygame.time.get_ticks()
    # Данная переменная принимает значения от 0 до 100 и в зависимости от LENGTH_OF_DAY изменяется с разной скоростью
    daytime = tics // (LENGTH_OF_DAY // 100)
    daytime %= 100
    if daytime == 100:
        day_number += 1

    # Отрисовка затемнения
    screen.blit(day_night_surface, (0, 0))

    # Отрисовка hud
    screen.blit(gui_surface, (0, 0))
    hud.draw(gui_surface, daytime, tics, player)

    # Отрисовка доступных для строительства построек
    screen.blit(buildings_choice_surface, (SIZE[0] // 2 - 65 * 2 // 2, SIZE[1] - 120))
    buildings_preset_drawer.draw(buildings_choice_surface)

    pygame.display.flip()
    clock.tick(60)
