from functions import *


# Класс для отрисовки Hud'а
class Hud:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.logger_font = pygame.font.Font(None, 30)

        self.tree_icon = load_image('tree_icon.png')
        self.tree_icon_rect = self.tree_icon.get_rect()
        self.tree_icon_rect.x = SIZE[0] - 120
        self.tree_icon_rect.y = SIZE[1] - 100

        self.stone_icon = load_image('stone_icon.png')
        self.stone_icon_rect = self.tree_icon.get_rect()
        self.stone_icon_rect.x = SIZE[0] - 120
        self.stone_icon_rect.y = SIZE[1] - 65

        self.day_night_gradient = load_image("gradient.png")
        self.day_night_gradient_rect = self.day_night_gradient.get_rect()
        self.day_night_gradient_rect.x = SIZE[0] - 122
        self.day_night_gradient_rect.y = SIZE[1] - 130

    def draw(self, surface, day_number, daytime, player):
        surface.fill(pygame.Color(0, 0, 0, 0))
        surface.blit(self.day_night_gradient, self.day_night_gradient_rect)

        pygame.draw.rect(surface,
                         pygame.Color((255, 255, 255)),
                         (SIZE[0] - 125 + daytime, SIZE[1] - 131, 6, 17), 0)

        text = self.font.render("Day " + str(day_number), 1, pygame.color.Color('white'))
        text_rect = text.get_rect()
        text_rect.x = SIZE[0] - 120
        text_rect.y = SIZE[1] - 150
        surface.blit(text, text_rect)

        # Текст, уведомляющий о начале или окончании ночи
        if int(daytime) in range(33, 40) or int(daytime) in range(80, 87):
            if int(daytime) in range(33, 40):
                text = self.logger_font.render('Night has come', 1, pygame.color.Color('white'))
            if int(daytime) in range(80, 87):
                text = self.logger_font.render('Night has ended', 1, pygame.color.Color('white'))
            text_rect = text.get_rect()
            text_rect.x = SIZE[0] // 2 - text_rect.w // 2
            text_rect.y = SIZE[1] - 600
            surface.blit(text, text_rect)

        wood_text = self.font.render(" — " + str(player.inventory['wood']), 1, pygame.color.Color('white'))
        wood_text_rect = text.get_rect()
        wood_text_rect.x = SIZE[0] - 80
        wood_text_rect.y = SIZE[1] - 90
        surface.blit(wood_text, wood_text_rect)

        stones_text = self.font.render(" — " + str(player.inventory['stones']), 1, pygame.color.Color('white'))
        stones_text_rect = stones_text.get_rect()
        stones_text_rect.x = SIZE[0] - 80
        stones_text_rect.y = SIZE[1] - 55
        surface.blit(stones_text, stones_text_rect)

        surface.blit(self.tree_icon, self.tree_icon_rect)
        surface.blit(self.stone_icon, self.stone_icon_rect)


# Класс для отрисовки серфейса выбора построек
class DrawBuildingsPresets:
    def __init__(self, player):
        # Словарь типов построек для отрисовки в hud'е
        self.types_of_buildings = {1: load_image('MainBuilding/1.png'),
                                   2: load_image('Стена 1.png'),
                                   3: load_image('DoubleBarrelTurretAnimations/down/double_barrel_turret.png')}
        self.selected_building = 0
        self.amount_of_buildings = len(self.types_of_buildings)
        self.building_choice_surface_coords = (SIZE[0] // 2 - 65 * self.amount_of_buildings // 2, SIZE[1] - 120)

        self.font = pygame.font.Font(None, 20)

        self.player = player

    # блит на скрин текста и изображения
    def text_and_image(self, i, surface):
        text = self.font.render(str(i), 1, pygame.color.Color('white'))
        text_rect = text.get_rect()
        text_rect.x = (i - 1) * 65 + 48
        text_rect.y = 43
        surface.blit(text, text_rect)

        image = self.types_of_buildings.get(i)
        image = pygame.transform.scale(image, (30, 30))
        image_rect = image.get_rect()
        image_rect.x = 17 + 65 * (i - 1)
        image_rect.y = 53
        surface.blit(image, image_rect)

    def draw(self, surface):
        surface.fill(pygame.Color(0, 0, 0, 0))
        for i in range(1, self.amount_of_buildings + 1):
            if self.selected_building == i:
                pygame.draw.rect(surface, pygame.color.Color(128, 128, 0), (65 * (i - 1) + 5, 40, 55, 55), 5)
            else:
                pygame.draw.rect(surface, pygame.color.Color(128, 128, 0), (65 * (i - 1) + 5, 40, 55, 55), 2)
            self.text_and_image(i, surface)

        if self.player.were_placed_main_building:
            pygame.draw.rect(surface, pygame.color.Color(128, 128, 0, 128), (5, 40, 57, 57), 0)
            self.text_and_image(1, surface)


# Класс для главного меню и паузы
class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self.font = pygame.font.SysFont(None, 60)
        # Реализация кнопок
        self.list_of_buttons = ['Quit', 'pass', 'Start game']
        self.number_of_button = len(self.list_of_buttons) - 1
        self.dict_of_buttons = {'Start game': self.start_game, 'pass': self.pas,
                                'Quit': self.quit, 'Continue': self.start_game}

        self.mainClock = pygame.time.Clock()

        # Логина, связанная со временем, необходимо было, чтобы во время паузы daytime не менялся
        self.menu_tics = pygame.time.get_ticks()
        self.pause_tics = 0
        self.tics_before_pause = 0
        self.is_menu = True
        self.is_paused = False

    def start_game(self):
        self.running = False

    # Заглушка
    def pas(self):
        print('passed')

    def quit(self):
        pygame.quit()
        sys.exit()

    # Метод для умного распредения кнопок по экрану и их отрисовки
    def draw_buttons(self):
        for i in range(len(self.list_of_buttons)):
            color = (255, 255, 255) if i != self.number_of_button else (255, 0, 0)
            text = self.list_of_buttons[i]

            text_obj = self.font.render(text, 1, color)
            text_rect = text_obj.get_rect()

            x = WINDOW_WIDTH // 2 - text_rect.size[0] // 2
            y = WINDOW_WIDTH // 2 - 40 * i + len(self.list_of_buttons) * 40 // 2 - 30

            text_rect.topleft = (x, y)
            self.screen.blit(text_obj, text_rect)

    # Цикл отвечающий за меню и паузу. навигация по стрелкам или W, A, S, D
    def main_menu(self):
        if self.is_paused:
            pygame.display.set_caption('Game is paused')
            self.list_of_buttons[-1] = 'Continue'
        else:
            pygame.display.set_caption('Main menu')

        while self.running:
            self.screen.fill((0, 0, 0))
            # Рассчеты, связанные со временем
            if self.is_paused:
                self.pause_tics = pygame.time.get_ticks() - self.tics_before_pause
            if self.is_menu:
                self.menu_tics = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.number_of_button = (self.number_of_button + 1) % (len(self.list_of_buttons))
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.number_of_button = self.number_of_button - 1\
                            if self.number_of_button > 0 else len(self.list_of_buttons) - 1
                    # Обработка нажатия кнопки
                    if event.key == pygame.K_RETURN:
                        selected_button = self.list_of_buttons[self.number_of_button]
                        if selected_button == 'Start game':
                            self.is_menu = False
                        self.dict_of_buttons[selected_button]()

            self.draw_buttons()

            pygame.display.update()
            self.mainClock.tick(60)