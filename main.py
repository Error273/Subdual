from classes import *

pygame.init()
pygame.display.set_caption('Subdual')
screen = pygame.display.set_mode(SIZE)

running = True

clock = pygame.time.Clock()

grid = Grid(100, 100)

player = Player(400, 400)

buildings = []

# позиция камеры
camera_x = (WINDOW_WIDTH - player.x * 2) // 2
camera_y = (WINDOW_HEIGHT - player.y * 2) // 2


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # если нажали на крестик, выходим
            running = False
            continue
        # если мы нажали на кнопку и сейчас можно строить
        if event.type == pygame.MOUSEBUTTONDOWN and player.get_is_building():
            x, y = event.pos
            # проверяем, строим ли мы внутри карты
            if camera_y <= y < camera_y + CELL_SIZE * grid.height - CELL_SIZE and \
                    camera_x <= x < camera_x + CELL_SIZE * grid.width - CELL_SIZE:
                # я не совсем понимаю, зачем отнимать от координаты мыши координаты камеры, но без этого не работает
                x -= camera_x
                y -= camera_y

                # привязываем постройку к сетке
                # TODO: показывать здание перед постройкой, отцентрированное по мыши с уменьшенной прозрачностью, чтобы
                #  было понятно что и куда ставить

                x = x // CELL_SIZE * CELL_SIZE
                y = y // CELL_SIZE * CELL_SIZE

                buildings.append(BaseBuilding(x, y, 50, 50))

        if event.type == pygame.KEYDOWN:
            # если нажата клавиша вниз, то начинаем движение
            if event.key == pygame.K_w and player.y >= 0:
                player.set_going_up(True)
            if event.key == pygame.K_a and player.x >= 0:
                player.set_going_left(True)
            if event.key == pygame.K_s and player.y < grid.height * CELL_SIZE:
                player.set_going_down(True)
            if event.key == pygame.K_d and player.x < grid.width * CELL_SIZE:
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
    # Условия для ограничения выхода за пределы поля
    if player.x <= 0:
        player.set_going_left(False)
    if player.x >= grid.width * CELL_SIZE - CELL_SIZE:
        player.set_going_right(False)
    if player.y <= 0:
        player.set_going_up(False)
    if player.y >= grid.height * CELL_SIZE - CELL_SIZE * 2:
        player.set_going_down(False)

    # если игрок двигается, то и камеру тоже нужно двигать за ним.
    if player.going_left:
        camera_x += PLAYER_MOVEMENT_SPEED
    if player.going_right:
        camera_x -= PLAYER_MOVEMENT_SPEED
    if player.going_up:
        camera_y += PLAYER_MOVEMENT_SPEED
    if player.going_down:
        camera_y -= PLAYER_MOVEMENT_SPEED

    screen.fill(BACKGROUND_COLOR)
    # показываем сетку только если сейчас можно строить
    if player.get_is_building():
        grid.render(screen, camera_x, camera_y)

    # отрисовываем все постройки
    for building in buildings:
        building.update()
        building.draw(screen, camera_x, camera_y)

    player.update()
    player.draw(screen, camera_x, camera_y)

    clock.tick(60)
    pygame.display.flip()
