import utils


class Cloud:
    current_clouds = []
    current_lightnings = []

    def __init__(self, map_obj):
        self.map = map_obj

    def generate_clouds(self, number_of_clouds):
        counter = 0
        while counter < number_of_clouds:
            x, y = utils.random_cord(self.map.width, self.map.length)
            if self.map.field[y][x] == 'grass':
                self.current_clouds.append([x, y])
                counter += 1

    def generate_lightnings(self, chance):
        clouds_index = []
        for i in range(len(self.current_clouds)):
            if utils.random_chance(chance):
                clouds_index.append(i)
                self.current_lightnings.append(self.current_clouds[i])
        self.current_clouds = [x for i, x in enumerate(self.current_clouds) if i not in clouds_index]

    def is_lightning(self, x, y):
        for lightning in self.current_lightnings:
            l_x, l_y = lightning
            if l_x == x and l_y == y:
                return True
        else:
            return False

    def update_clouds(self, number_of_clouds, lightning_chance):
        self.current_clouds = []
        self.current_lightnings = []
        self.generate_clouds(number_of_clouds)
        self.generate_lightnings(lightning_chance)
