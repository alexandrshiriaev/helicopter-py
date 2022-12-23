from utils import load_json


def get_settings():
    return load_json('generation_settings.json')
