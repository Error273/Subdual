from classes import *

pygame.init()
screen = pygame.display.set_mode(SIZE)

running = True

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()

grid = Grid(100, 100, all_sprites)

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
            if player.get_is_building():
                if event.button == 1:  # если нажали на левую кнопку
                    # проверяем, строим ли мы внутри карты
                    if grid.rect.top <= y <= grid.rect.bottom - CELL_SIZE and \
                            grid.rect.left <= x < grid.rect.right - CELL_SIZE:

                        # привязываем постройку к сетке
                        # TODO: показывать здание перед постройкой, отцентрированное по мыши с уменьшенной
                        #  прозрачностью, чтобы было понятно что и куда ставить

                        # умным образом отравниваем построку по сетке
                        # FIXME: не всегда хорошо работает
                        x = x - x % CELL_SIZE + grid.rect.x % CELL_SIZE
                        y = y - y % CELL_SIZE + grid.rect.y % CELL_SIZE

                        building = WoodenFence(x, y, buildings_group, all_sprites)
                        # проверяем, сколько объектов находится на месте постройки. пропускаем 2 потому, что это сетка и
                        # (почему - то) сама постройка
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
                            not player.get_is_building():
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

            # если нажали на клавишу 1, то переключаем режим строительства
            if event.key == pygame.K_1:
                player.set_is_building(not player.get_is_building())

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
    print(player.inventory)

    # FIXME: при движении игрок сам сдвигается в сторону движения, то есть его координаты на экране меняются (а они не
    # должны, так как камерой мы фокусим игрока)
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    # показываем сетку только если сейчас можно строить
    if player.get_is_building():
        grid.draw(screen)

    # отрисовываем все постройки
    buildings_group.update()
    buildings_group.draw(screen)

    # Обновляем и отрисовывем игрока
    player_group.update(grid, buildings_group)
    player_group.draw(screen)

    pygame.display.flip()
    clock.tick(60)
