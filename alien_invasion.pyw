from scoreboard import Scoreboard
from game_stats import GameStats
from settings import Settings
from button import Button
from bullet import Bullet
from alien import Alien
from time import sleep
from ship import Ship
import pygame
import sys


class AlienInvasion:
    '''Класс для управления ресурсами и поведением игры.'''

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Alien Invasion')
        self.settings = Settings()
        self.resolution = (self.settings.screen_width,
                           self.settings.screen_height)

        self.screen = pygame.display.set_mode(self.resolution)
        # self.screen = pygame.display.set_mode(
        #     (0, 0), pygame.FULLSCREEN)

        # получить параметры полноэкранного режима и передать в настройки
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        icon = pygame.image.load('images/icon.png')
        pygame.display.set_icon(icon)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.clock = pygame.time.Clock()
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.play_easy = Button(self, 'Easy')
        self.play_easy.button_color = (250, 128, 0)
        self.play_easy.rect.x -= 300
        self.play_easy.msg_image_rect.x -= 300

        self.play_button = Button(self, 'Normal')

        self.play_hard = Button(self, 'Hard')
        self.play_hard.button_color = (250, 0, 0)
        self.play_hard.rect.x += 300
        self.play_hard.msg_image_rect.x += 300

    def run_game(self):
        '''Запуск основного цикла игры.'''
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))  # проверка количества выпущенных снарядов
        # Удаление снарядов и пришельцев, участвующих в коллизиях
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            # self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.sb.check_high_score()
        if not self.aliens:  # пуста ли группа aliens
            self.bullets.empty()  # удаляет все существующие спрайты из группы
            self._create_fleet()
            self.settings.increase_speed()
            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()

    def _check_events(self):
        # Отслеживание событий клавиатуры и мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            # print(event)

    def _check_play_button(self, mouse_pos):
        '''Запускает новую игру при нажатии кнопки Play'''
        play_easy = self.play_easy.rect.collidepoint(mouse_pos)
        play_normal = self.play_button.rect.collidepoint(mouse_pos)
        play_hard = self.play_hard.rect.collidepoint(mouse_pos)

        clicked = play_easy or play_normal or play_hard

        if clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_setting()
            pygame.mouse.set_visible(False)  # Указатель мыши скрывается
            self.stats.reset_stats()
            if play_normal:
                # print('normal mode')
                pass
            elif play_easy:
                self.settings.speedup_scale = 1.1
                # print('easy mode')
            elif play_hard:
                self.settings.speedup_scale = 2.1
                # print('hard mode')
            self.start_game()

    def start_game(self):
        self.stats.reset_stats()  # Сброс игровой статистики
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.stats.game_active = True
        self.aliens.empty()  # Очистка списков пришельцев
        self.bullets.empty()  # и снарядов
        self._create_fleet()  # Создание нового флота
        self.ship.center_ship()  # и размещение корабля в центре
        self.settings.initialize_dynamic_setting()

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        if event.key == pygame.K_q:
            sys.exit()
        if event.key == pygame.K_p:
            self.start_game()
        if event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_screen(self):
        # Отображение последнего прорисованного экрана
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()

        # Кнопка Play отображается в том случае, если игра неактивна
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.play_easy.draw_button()
            self.play_hard.draw_button()

        pygame.display.flip()
        self.clock.tick(144)

    def _fire_bullet(self):
        '''Создание нового снаряда и включение его в группу bullets'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        '''Создание флота пришельцев'''
        # создание пришельца
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_alines_x = available_space_x // (2 * alien_width)

        '''Определяет количество рядов, помещающихся на экране.'''
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             3*alien_height - ship_height)

        number_rows = available_space_y // (2 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_alines_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_alines_x = available_space_x // (2 * alien_width)
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _update_aliens(self):
        '''Обновляет позиции всех пришельцев во флоте'''
        self._check_fleet_edges()
        self.aliens.update()
        # Проверка коллизий 'пришелец — корабль'
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            # print('ship hit!')
            self._ship_hit()
        self._check_aliens_bootom()

    def _ship_hit(self):
        '''Обрабатывает столкновение корабля с пришельцем'''
        if self.stats.ships_left > 0:
            # Уменьшение ships_left
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()
            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()
            # Пауза
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bootom(self):
        '''Проверяет, добрались ли пришельцы до нижнего края экрана'''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
