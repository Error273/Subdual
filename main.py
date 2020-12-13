import pygame
from classes import *

pygame.init()
pygame.display.set_caption('Subdual')
screen = pygame.display.set_mode(SIZE)

running = True

clock = pygame.time.Clock()

grid = Grid(100, 100)

player = Player(400, 300)

# позиция камеры
camera_x = 0
camera_y = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # если нажали на крестик, выходим
            running = False
            continue
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
    # если игрок двигается, то и камеру тоже нужно двигать за ним.
    if player.going_left:
        camera_x += PLAYER_MOVEMENT_SPEED
    if player.going_right:
        camera_x -= PLAYER_MOVEMENT_SPEED
    if player.going_up:
        camera_y += PLAYER_MOVEMENT_SPEED
    if player.going_down:
        camera_y -= PLAYER_MOVEMENT_SPEED


    # Условия для ограничения выхода за пределы поля
    if player.x < 0:
        player.set_going_left(False)
    if player.x >= grid.width * CELL_SIZE - CELL_SIZE:
        player.set_going_right(False)
    if player.y - CELL_SIZE < 0:
        player.set_going_up(False)
    if player.y >= grid.height * CELL_SIZE - CELL_SIZE:
        player.set_going_down(False)

    screen.fill(BACKGROUND_COLOR)
    print(player.x, player.y, ' --->', camera_x, camera_y)

    # захват камерой получается при смещении каждого объекта на экране на координаты камеры
    # поэтому для каждого объекта
    grid.render(screen, camera_x, camera_y)

    player.update()
    player.draw(screen, camera_x, camera_y)

    clock.tick(60)
    pygame.display.flip()
