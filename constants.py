# размер окна
SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800

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

# Продолжительность дня в тиках
LENGTH_OF_THE_DAY = 20000 // 5

# переменная, на основе которой высчитывается количество противников в конкретный день. чем больше - тем больше врагов
COMPLICATION_COEF = 4

#  максимальное количество противников, находящихся на карте
MAX_ENEMIES_AMOUNT = 200

# здоровье главной постройки
MAIN_BUILDING_HEALTH = 1000

# здоровье деревянного забора
WOODEN_FENCE_HEALTH = 200

# характеристики турели. переменные говорят сами за себя
DOUBLE_BARREL_TURRET_SHOOTING_SPEED = 15
DOUBLE_BARREL_TURRET_SHOOTING_RADIUS = 200
DOUBLE_BARREL_TURRET_DAMAGE = 10
DOUBLE_BARREL_TURRET_HEALTH = 200

# характеристики обычного противника
CAMEL_MOVING_SPEED = 1
CAMEL_HEALTH = 150
CAMEL_DAMAGE = 10
CAMEL_ATTACK_SPEED = 10

# характеристики противника, атакующего издалека
TACTICAL_CAMEL_MOVING_SPEED = 1
TACTICAL_CAMEL_HEALTH = 100
TACTICAL_CAMEL_DAMAGE = 20
TACTICAL_CAMEL_ATTACK_SPEED = 50
TACTICAL_CAMEL_ATTACK_RADIUS = 100
