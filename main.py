from game_classes import *
from hud_classes import *

pygame.init()

# инициализируем миксер, создаем 8 каналов
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

# инициализация звуковых каналов
# канал для ходьбы игрока
player_walking_channel = pygame.mixer.Channel(1)
# канал отдельно для турелей, так как они издают много звуков
turrets_channel = pygame.mixer.Channel(2)
# канал для врагов, чтобы не перебивали все остальное
enemies_channel = pygame.mixer.Channel(3)
# канал для звуков установки/разрушения построек игроком
building_destroying_channel = pygame.mixer.Channel(4)

screen = pygame.display.set_mode(SIZE)

# работает ли игра
running = True
clock = pygame.time.Clock()
tics = 0  # тики, прошедшие с начала игры
daytime = 0  # время суток
day_number = 1  # количество пройденных дней
enemies_were_spawn = False  # были ли заспавнены враги за последние сутки. нужно, чтобы враги не спавнили дважды

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

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
    rock = spawn_object(Rock, buildings_group, all_sprites,
                        min_x=0, min_y=0,
                        max_x=grid.width * CELL_SIZE - 75,
                        max_y=grid.height * CELL_SIZE - 75,
                        collide_group=buildings_group)

# генерируем деревья
for _ in range(TREES_AMOUNT):
    # вычитаем 50 и 75, так как мы не хотим, чтобы дерево выходило за границы поля
    tree = spawn_object(Tree, buildings_group, all_sprites,
                        min_x=0, min_y=0,
                        max_x=grid.width * CELL_SIZE - 50,
                        max_y=grid.height * CELL_SIZE - 75,
                        collide_group=buildings_group)

player = spawn_object(Player, player_walking_channel, all_sprites, player_group,
                      min_x=0, min_y=0,
                      max_x=grid.width * CELL_SIZE - 25,
                      max_y=grid.height * CELL_SIZE - 50,
                      collide_group=buildings_group)

hud = Hud()
buildings_preset_drawer = DrawBuildingsPresets(player)

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

                        # проверяем тип потенциальной постройки, чтобы не поставить главную постройку дважды
                        if player.get_potential_building() == MainBuilding:
                            if not player.were_placed_main_building:
                                building = player.get_potential_building()(x, y, buildings_group, all_sprites)
                                building.set_sound_channel(building_destroying_channel)
                                player.were_placed_main_building = True
                        else:
                            building = player.get_potential_building()(x, y, buildings_group, all_sprites)

                            # если постройка туруль, то устанавливаем ей звковой канал специально для турелей,
                            # иначе - для всего сотавльного
                            if type(building) == DoubleBarrelTurret:
                                building.set_sound_channel(turrets_channel)
                            else:
                                building.set_sound_channel(building_destroying_channel)

                        # проверяем, сколько объектов находится на месте постройки. пропускаем 2 потому, что это сетка и
                        # сама постройка
                        if len(pygame.sprite.spritecollide(building, all_sprites, False)) > 2:
                            # удаляем построку совсем
                            building.kill()
                            # если мы пытались построить главное здание, то нужно вернуть возмжность ее заного поставить
                            if type(building) == MainBuilding:
                                player.were_placed_main_building = False
                        else:
                            # если поставили главное здание, то выключаем режим постройки
                            if type(building) == MainBuilding:
                                player.set_potential_building(None)
                            # играем звук постройки
                            building.play_building_sound()


                elif event.button == 3:  # если нажали на правую кнопку мыши, то построку стоит удалить
                    for building in buildings_group:
                        # находим постройку, с которой соприкасается курсор и удаляем ее, если она не главное здание
                        # (по задумке главное здание нельзя убрать)
                        if building.rect.collidepoint(x, y) and building.building_type == 'PlayerBuilding' and \
                                type(building) != MainBuilding:
                            # играем звук уничтожения
                            building.play_destroying_sound()
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
            if event.key in range(pygame.K_1, pygame.K_3 + 1):
                buildings_preset_drawer.selected_building = event.key - 48
                if player.get_potential_building():  # если режим строительства уже включен, то его нужно выключить
                    buildings_preset_drawer.selected_building = 0
                    player.set_potential_building(None)
                # Проверка необходимости активации режима постройки для MainBuilding
                elif player.were_placed_main_building and event.key == pygame.K_1:
                    buildings_preset_drawer.selected_building = 0
                else:
                    # выбираем главное здание
                    if event.key == pygame.K_1:
                        player.set_potential_building(MainBuilding)
                    # выбираем забор
                    if event.key == pygame.K_2:
                        player.set_potential_building(WoodenFence)
                    # выбираем турель
                    elif event.key == pygame.K_3:
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
    buildings_group.update(enemies_group)
    buildings_group.draw(screen)

    # Обновляем и отрисовывем игрока
    player_group.update(grid, buildings_group)
    player_group.draw(screen)

    enemies_group.update(buildings_group)
    enemies_group.draw(screen)

    saturation_coef = calculate_night_saturation_coef(daytime)
    # Затемнение поля
    pygame.draw.rect(day_night_surface, pygame.Color(15, 32, 161, int(saturation_coef)), (0, 0, SIZE[0], SIZE[1]), 0)

    # Расчеты, связанные с циклом дня и ночи
    tics = pygame.time.get_ticks()
    # Данная переменная принимает значения от 0 до 100 и в зависимости от LENGTH_OF_DAY изменяется с разной скоростью
    daytime = tics // (LENGTH_OF_THE_DAY // 100)
    daytime %= 100

    # если наступил новый день, то сбрасываем возможность спавна врагов и удаляем всех врагов, находящихся за экраном
    # (повышает производительность)
    if day_number != tics // LENGTH_OF_THE_DAY:
        enemies_were_spawn = False
        [enemy.kill() for enemy in enemies_group if get_distance(player, enemy) > max([WINDOW_HEIGHT, WINDOW_WIDTH])]
        # обновляем день
        day_number = tics // LENGTH_OF_THE_DAY
    # если мы построили главное здание, можно спавнить врагов в определенное время суток
    if daytime in range(33, 50) and player.were_placed_main_building and not enemies_were_spawn:
        enemies_were_spawn = spawn_enemies(day_number, buildings_group, enemies_group, enemies_channel,
                                           enemies_group, all_sprites,
                                           grid=grid)

    # Отрисовка затемнения
    screen.blit(day_night_surface, (0, 0))

    # Отрисовка hud
    screen.blit(gui_surface, (0, 0))
    hud.draw(gui_surface, day_number, daytime, player)

    # Отрисовка доступных для строительства построек
    screen.blit(buildings_choice_surface, (SIZE[0] // 2 - 65 * 2 // 2, SIZE[1] - 120))
    buildings_preset_drawer.draw(buildings_choice_surface)

    pygame.display.flip()
    clock.tick(60)
