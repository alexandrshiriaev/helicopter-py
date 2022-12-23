from emoji_symbols import get_symbols
import utils
from get_shop import shop_settings
from cloud import Cloud

Symbols = get_symbols()


class Map:
    field = []
    width, length = 0, 0
    trees_cords = []
    helicopter = None
    shop = None
    clouds = None
    hospital = None

    def __init__(self, gen_set):
        self.gen_set = gen_set
        self.width, self.length = gen_set['field_width'], gen_set['field_length']
        self.generate_field(self.width, self.length)
        self.clouds = Cloud(self)

    def set_helicopter(self, obj):
        self.helicopter = obj

    def generate_field(self, width, length):
        self.field = [['grass' for i in range(width)] for j in range(length)]

    def generate_trees(self, tree_chance):
        for i in range(len(self.field)):
            for j in range(len(self.field[i])):
                if utils.random_chance(tree_chance) and self.field[i][j] == 'grass':
                    self.field[i][j] = 'tree'
                    self.trees_cords.append((j, i))

    def generate_tree(self):
        x, y = utils.random_cord(self.width, self.length)
        while True:
            if self.field[y][x] == 'grass':
                self.set_tree(x, y)
                break
            else:
                x, y = utils.random_cord(self.width, self.length)

    def generate_shop(self):
        settings = shop_settings()
        self.shop = {
            'current_level': 0,
            'shop_levels': settings,
            'cords': utils.random_cord(self.width, self.length)
        }
        x, y = self.shop['cords']
        self.field[y][x] = 'money'

    def generate_hospital(self):
        self.hospital = {
            'heal_cost': self.helicopter.settings['heal_cost']
        }
        while True:
            x, y = utils.random_cord(self.width, self.length)
            if self.field[y][x] == 'grass':
                self.hospital['cords']: [x, y]
                break
        self.field[y][x] = 'hospital'

    def set_tree(self, x, y):
        self.field[y][x] = 'tree'
        self.trees_cords.append((x, y))

    def generate_river(self, river_length):
        x, y = utils.random_cord(self.width, self.length)
        self.field[y][x] = 'water'
        count = 0
        while count < river_length - 1:
            x_new, y_new = utils.neighboring_coord(x, y)
            if utils.in_field(self.width, self.length, x_new, y_new):
                if self.field[y][x] != 'water':
                    count += 1
                self.field[y][x] = 'water'
                x, y = x_new, y_new

    def generate_fire(self, obj):
        if not len(self.trees_cords):
            return
        cords, index = utils.random_element(self.trees_cords)
        x, y = cords
        self.field[y][x] = 'fire'
        obj.add_event(self.gen_set['fire_out'] + obj.tick, self.process_fire, [x, y, obj])
        self.trees_cords.pop(index)

    def get_cell(self, x, y):
        return self.field[y][x]

    def process_fire(self, x, y, obj, was_extinguished=False):
        if self.field[y][x] == 'fire' and not was_extinguished:
            self.field[y][x] = 'grass'
            self.helicopter.damage(1)
        elif self.field[y][x] == 'fire' and was_extinguished:
            self.set_tree(x, y)
        event_list = obj.tick_events[str(self.gen_set['fire_out'])]
        event_list = [event for event in event_list if not utils.is_equal(event[1][0:2], [x, y])]
        obj.tick_events[str(self.gen_set['fire_out'])] = event_list

    def export_data(self):
        data = {'shop_level': self.shop['current_level']}
        return data

    def import_data(self, data):
        self.shop['current_level'] = data['shop_level']


def convert_to_emoji(field_arr):
    new_field = [[Symbols[symbol] for symbol in row] for row in field_arr]
    return new_field
