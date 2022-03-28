import os.path
import json


PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))


def load_json_data(rel_path):
    path = os.path.join(PACKAGE_DIR, rel_path)
    with open(path, encoding='utf-8') as inp:
        return json.load(inp)


SMARTPHONE_DEV_IDS = load_json_data('data/smartphone_dev_id.json')
TABLET_DEV_IDS = load_json_data('data/tablet_dev_id.json')
