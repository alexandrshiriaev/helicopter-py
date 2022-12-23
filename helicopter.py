import utils
from helicopter_behaviour import get_settings


class Helicopter:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.settings = get_settings()
        self.water_capacity = self.settings['water_capacity']
        self.current_water = self.settings['start_water']
        self.max_health = self.settings['max_health']
        self.current_health = self.max_health
        self.can_fill = True
        self.score = 0
        self.money = 0
        self.gameover_func = None

    def move(self, x_offset, y_offset, field_width, field_length, callback_funcs):
        if utils.in_field(field_width, field_length, self.x + x_offset, self.y + y_offset):
            self.x += x_offset
            self.y += y_offset
            for func in callback_funcs:
                func[0](*func[1])

    def damage(self, hp):
        self.set_health(self.current_health - hp)

    def put_out(self, callback_funcs):
        cost = self.settings['extinguishing_cost']
        if self.current_water - cost >= 0:
            self.current_water -= self.settings['extinguishing_cost']
            for func in callback_funcs:
                func[0](*func[1])

    def fill_water(self, add_event, get_current_tick, event_list):
        if self.current_water < self.water_capacity:
            self.current_water += 10
            self.can_fill = False
            if self.current_water > self.water_capacity:
                self.current_water = self.water_capacity
            add_event((get_current_tick() + self.settings['fill_cooldown']), self.switch_can_fill,
                      [get_current_tick() + self.settings['fill_cooldown'], event_list])

    def try_fill(self, get_cell, add_event, get_current_tick, tick_events):
        if get_cell(self.x, self.y) == 'water' and self.can_fill:
            self.fill_water(add_event, get_current_tick, tick_events)

    def switch_can_fill(self, func_tick, tick_events):
        if not self.can_fill:
            event_list = tick_events[str(func_tick)]
            event_list = [event for event in event_list if event[0] == func_tick]
            tick_events[str(func_tick)] = event_list
            self.can_fill = not self.can_fill

    def increase_level(self, shop):
        if shop['current_level'] < len(shop['shop_levels']):
            current_level = list(shop['shop_levels'].items())[shop['current_level']]
            if self.money >= int(current_level[0]):
                self.water_capacity = current_level[1]
                self.current_water = self.water_capacity
                shop['current_level'] += 1
                self.money -= int(current_level[0])

    def gain_score(self, score):
        self.score += score
        self.gain_money(score)

    def gain_money(self, money):
        self.money += money

    def set_health(self, health):
        if health < 0:
            self.current_health = 0
        elif health > self.max_health:
            self.current_health = self.max_health
        else:
            self.current_health = health
        if self.current_health == 0:
            self.gameover_func()

    def try_heal(self, hp, cost):
        if self.money >= cost and self.current_health < self.max_health:
            self.money -= cost
            self.set_health(self.current_health + hp)

    def get_stats(self):
        return {"health": [self.current_health, self.max_health],
                "water": [self.current_water, self.water_capacity],
                "score": self.score,
                "money": self.money
                }

    def get_cords(self):
        return self.x, self.y

    def export_data(self):
        data = {'current_water': self.current_water,
                'water_capacity': self.water_capacity,
                'score': self.score,
                'current_health': self.current_health,
                }
        return data

    def import_data(self, data):
        self.current_water = data['current_water']
        self.water_capacity = data['water_capacity']
        self.score = data['score']
        self.current_health = data['current_health']
