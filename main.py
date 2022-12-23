import copy
import time
import json

import utils
from utils import clear
from map import Map
from map import convert_to_emoji
from gen_settings import get_settings
from control_keys import get_controls
from helicopter import Helicopter
from controller import Controller
from emoji_symbols import get_symbols
import saves

generation_settings = get_settings()
control_keys = get_controls()

emoji = get_symbols()


class Game:
    tick_events = {

    }

    def add_event(self, tick, func, args: list):
        """
            Добавляет новое событие по тикам в список
        """
        if str(tick) in self.tick_events:
            self.tick_events[str(tick)] = [[func, args]] + self.tick_events[str(tick)]
        else:
            self.tick_events[str(tick)] = [[func, args]]

    def __init__(self, gen_set):
        # Текущий тик
        self.tick = 0

        # Инициализируем карту и вертолёт
        self.map = Map(generation_settings)
        self.helicopter = Helicopter(*utils.random_cord(self.map.width, self.map.length))
        self.helicopter.gameover_func = self.game_over
        self.map.set_helicopter(self.helicopter)

        self.controller = Controller()
        self.load_settings(control_keys)

        # Генерируем ландшафт
        self.map.generate_river(gen_set['river_length'])
        self.map.generate_shop()
        self.map.generate_hospital()
        self.map.generate_trees(gen_set['tree_chance'])
        self.map.generate_fire(self)
        self.map.clouds.generate_clouds(gen_set['number_of_clouds'])
        self.map.clouds.generate_lightnings(gen_set['lightning_chance'])

        # Создаём события
        self.add_event(gen_set['clouds_update'], self.map.clouds.update_clouds, [gen_set['number_of_clouds'],
                                                                                 gen_set['lightning_chance']])
        self.add_event(gen_set['generate_fire'], self.map.generate_fire, [self])
        self.add_event(gen_set['generate_fire'], self.map.generate_fire, [self])
        self.add_event(gen_set['generate_tree'], self.map.generate_tree, [])
        self.add_event(gen_set['generate_tree'], self.map.generate_tree, [])
        self.add_event(1, self.helicopter.try_fill,
                       [self.map.get_cell, self.add_event, self.get_current_tick, self.tick_events])

        # Рендерим поле
        self.render(self.map.field)

    def render(self, field):
        """
        Выводит поле в консоль
        """
        while True:
            clear()  # Очищаем консоль каждый тик
            field_copy = copy.deepcopy(field)  # Создаём копию поля
            field_copy[self.helicopter.y][
                self.helicopter.x] = 'helicopter'  # Заменяем в точке координат вертолёта клетку поля на вертолёт
            self.overlay_clouds(field_copy, self.map.clouds)
            converted_field = convert_to_emoji(field_copy)  # Конвертируем поле в эмодзи
            print(f'TICK: {self.tick}')  # Выводим тики
            helicopter_stats = self.helicopter.get_stats()
            print(
                f'{emoji["tank"]}: {helicopter_stats["water"][0]} / {helicopter_stats["water"][1]}')  # Выводим количество воды в баке
            print(
                f'{emoji["heart"]}: {helicopter_stats["health"][0]} / {helicopter_stats["health"][1]}')  # Выводим здоровье
            print(
                f'{emoji["score"]}: {helicopter_stats["score"]}')
            print(
                f'{emoji["money"]}: {helicopter_stats["money"]}')

            print(emoji['border'] * (self.map.length + 2))
            for row in converted_field:  # Циклом проходим по списку строк поля и выводим их
                print(emoji['border'], end='')
                print(*row, sep='', end='')
                print(emoji['border'])
            print(emoji['border'] * (self.map.length + 2))
            self.inc_tick()  # Увеличиваем тик на 1

            time.sleep(1 / 15)

    def helicopter_movements(self):
        x, y = self.helicopter.x, self.helicopter.y
        if self.map.field[y][x] == 'fire':
            self.helicopter.put_out([[self.map.process_fire, [x, y, self, True]], [self.helicopter.gain_score, [100]]])
        elif self.map.field[y][x] == 'money':
            self.helicopter.increase_level(self.map.shop)
        elif self.map.field[y][x] == 'hospital':
            self.helicopter.try_heal(1, self.map.hospital['heal_cost'])
        elif self.map.clouds.is_lightning(x, y):
            self.helicopter.damage(1)

    def overlay_clouds(self, field, cloud_obj):
        for cords in cloud_obj.current_clouds:
            x, y = cords
            field[y][x] = 'cloud'
        for cords in cloud_obj.current_lightnings:
            x, y = cords
            field[y][x] = 'lightning'

    def inc_tick(self):
        self.tick += 1
        for event_tick in self.tick_events.copy():
            if self.tick % int(event_tick) == 0:
                for event_arr in self.tick_events[event_tick]:
                    event_arr[0](*event_arr[1])

    def get_current_tick(self):
        return self.tick

    def game_over(self):
        clear()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("X X X X X X        X X X X  X")
        print("X GAME OVER, YOUR SCORE IS", self.helicopter.score, " X")
        print("X X X X X X        X X X X  X")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        input('Click Enter to exit...')
        exit(0)

    def load_settings(self, settings_dict):
        """
        Загружает клавиши управления и создаёт события при нажатии на клавиши
        """
        for k, v in settings_dict.items():
            match k:
                case 'forward':
                    for i in v:
                        self.controller.add_key_event(i, self.helicopter.move, [0, -1, self.map.width, self.map.length,
                                                                                [[self.helicopter_movements, []]]])
                case 'backward':
                    for i in v:
                        self.controller.add_key_event(i, self.helicopter.move, [0, 1, self.map.width, self.map.length,
                                                                                [[self.helicopter_movements, []]]])
                case 'left':
                    for i in v:
                        self.controller.add_key_event(i, self.helicopter.move, [-1, 0, self.map.width, self.map.length,
                                                                                [[self.helicopter_movements, []]]])
                case 'right':
                    for i in v:
                        self.controller.add_key_event(i, self.helicopter.move, [1, 0, self.map.width, self.map.length,
                                                                                [[self.helicopter_movements, []]]])
                case 'load':
                    for i in v:
                        self.controller.add_key_event(i, self.import_data, [])

                case 'save':
                    for i in v:
                        self.controller.add_key_event(i, self.export_data, [])

    def export_data(self):
        data = {
            'helicopter': self.helicopter.export_data(),
            'map': self.map.export_data()
        }
        saves.make_save(data)

    def import_data(self):
        try:
            data = saves.load_save()
            helicopter_data = data['helicopter']
            map_data = data['map']
            self.helicopter.import_data(helicopter_data)
            self.map.import_data(map_data)
        except Exception:
            pass


def run():
    return Game(generation_settings)


if __name__ == '__main__':
    run()
