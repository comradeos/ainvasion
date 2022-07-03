import json


class GameStats():
    def __init__(self, ai_game):
        '''Инициализирует статистику'''
        self.settings = ai_game.settings
        # Игра Alien Invasion запускается в неактивном состоянии
        self.game_active = False
        self.reset_stats()

        # Рекорд не должен сбрасываться
        self.high_score = 0
        with open('high_score.json', 'r') as f:
            self.high_score = json.load(f)

    def reset_stats(self):
        '''Инициализирует статистику, изменяющуюся в ходе игры'''
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
