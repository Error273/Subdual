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

    def draw(self, surface, daytime, tics, player):
        surface.fill(pygame.Color(0, 0, 0, 0))
        surface.blit(self.day_night_gradient, self.day_night_gradient_rect)

        pygame.draw.rect(surface,
                         pygame.Color((255, 255, 255)),
                         (SIZE[0] - 125 + daytime, SIZE[1] - 131, 6, 17), 0)

        text = self.font.render("Day " + str(tics // LENGTH_OF_DAY + 1), 1, pygame.color.Color('white'))
        text_rect = text.get_rect()
        text_rect.x = SIZE[0] - 80
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
    def __init__(self):
        # Словарь типов построек для отрисовки в hud'е
        self.types_of_buildings = {1: load_image('Стена 1.png', -1),
                                   2: load_image('DoubleBarrelTurretAnimations/down/double_barrel_turret.png', -1)}
        self.selected_building = 0
        self.amount_of_buildings = len(self.types_of_buildings)
        self.building_choice_surface_coords = (SIZE[0] // 2 - 65 * self.amount_of_buildings // 2, SIZE[1] - 120)

        self.font = pygame.font.Font(None, 20)

    def draw(self, surface):
        surface.fill(pygame.Color(0, 0, 0, 0))
        for i in range(1, self.amount_of_buildings + 1):
            if self.selected_building == i:
                pygame.draw.rect(surface, pygame.color.Color(128, 128, 0), (65 * (i - 1) + 5, 40, 55, 55), 5)
            else:
                pygame.draw.rect(surface, pygame.color.Color(128, 128, 0), (65 * (i - 1) + 5, 40, 55, 55), 2)

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
