import random
import json
from os import system, name


def clear():
    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')


def in_field(width, length, x, y):
    return 0 <= x < width and 0 <= y < length


def random_chance(chance):
    return chance >= random.random()


def neighboring_coord(x, y):
    cords_arr = [[x - 1, y], [x, y - 1], [x + 1, y], [x, y + 1]]
    return cords_arr[random.randint(0, 3)]


def random_cord(width, length):
    return random.randint(0, width - 1), random.randint(0, length - 1)


def random_element(arr):
    rand_index = random.randint(0, len(arr) - 1)
    return arr[rand_index], rand_index


def is_equal(arr1, arr2):
    return " ".join([str(i) for i in arr1]) == " ".join([str(i) for i in arr2])


def load_json(path):
    # 🌲🌊🚁🟩🔥🏥💛💵🧳🏆⚡️⛅️🔲⬛️
    with open(path, "r", encoding='utf-8') as read_file:
        data = json.load(read_file)

    return data


def dump_json(path, data):
    with open(path, "w", encoding='utf-8') as write_file:
        json.dump(data, write_file)
