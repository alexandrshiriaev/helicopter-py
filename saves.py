import utils


def make_save(data):
    utils.dump_json('current_save.json', data)


def load_save():
    data = utils.load_json('current_save.json')
    return data
