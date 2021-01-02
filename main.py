from classes import *

pygame.init()
screen = pygame.display.set_mode(SIZE)

running = True

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
buildings_group = pygame.sprite.Group()

grid = Grid(100, 100, all_sprites)

player = Player(400, 400, all_sprites, player_group)

camera = Camera()

while running:
    # выводим фпс в название окна
    pygame.display.set_caption(str(clock.get_fps()))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # если нажали на крестик, выходим
            running = False
            continue

        # если мы нажали на кнопку и сейчас можно строить
        if event.type == pygame.MOUSEBUTTONDOWN and player.get_is_building():
            x, y = event.pos
            # проверяем, строим ли мы внутри карты
            if grid.rect.top <= y <= grid.rect.bottom - CELL_SIZE and \
                    grid.rect.left <= x < grid.rect.right - CELL_SIZE:

                # привязываем постройку к сетке
                # TODO: показывать здание перед постройкой, отцентрированное по мыши с уменьшенной прозрачностью, чтобы
                #  было понятно что и куда ставить

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
            # если нажали на клавишу один, то переключаем режим строительства
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
