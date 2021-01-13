# размер окна
SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 900

# размер одной клетки. изменять нельзя, нужен для легкости чтения кода.
CELL_SIZE = 25

# цвет заднего фона
BACKGROUND_COLOR = (68, 100, 58)
# скорость перемещения игрока
PLAYER_MOVEMENT_SPEED = 5

# количество деревьев на карте
TREES_AMOUNT = 50
# количество камней на карте
ROCKS_AMOUNT = 15

# минимальное расстояние от игрока до ресурса (в пикселях), необходимое для добычи
MINING_DISTANCE = 100
# скорость добычи ресурсов (сколько тактов должно пройти, чтобы ресурс добавился в инвентарь)
MINING_SPEED = 10

# Количество типов построек
AMOUNT_OF_BUILDINGS = 2
# Начальные координаты слоя для типов построек
BUILDING_CHOICE_SURFACE_COORDS = (SIZE[0] // 2 - 65 * AMOUNT_OF_BUILDINGS // 2, SIZE[1] - 120)

DAYTIME = 100