import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    '''Класс управления кораблем'''

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        # Загружает изображение корабля и получает прямоугольник
        self.image = pygame.image.load('images/ship.png')
        self.rect = self.image.get_rect()
        # Каждый новый корабль появляется у нижнего края экрана
        self.rect.midbottom = self.screen_rect.midbottom

        self.moving_right = False
        self.moving_left = False

        # Сохранение вещественной координаты центра корабля
        self.x = float(self.rect.x)

    def update(self):
        if self.moving_right == True and self.rect.right < (self.screen_rect.right + 30):
            # print(f'right: {self.rect.x}')
            self.x += self.settings.ship_speed_factor

        if self.moving_left == True and self.rect.left > (self.screen_rect.left - 30):
            # print(f'left: {self.rect.x}')
            self.x -= self.settings.ship_speed_factor

        self.rect.x = self.x
        # print(self.rect)

    def blitme(self):
        '''Рисует корабль в текущей позиции'''
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
        pass
