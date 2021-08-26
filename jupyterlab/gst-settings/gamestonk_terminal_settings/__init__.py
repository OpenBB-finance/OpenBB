from .handlers import TerminalSettingsHandler
import json
import os.path as osp

from ._version import __version__

HERE = osp.abspath(osp.dirname(__file__))

with open(osp.join(HERE, 'labextension', 'package.json')) as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        'src': 'labextension',
        'dest': data['name']
    }]

def load_jupyter_server_extension(server_app):
    handlers = [("/gamestonk/settings", TerminalSettingsHandler)]
    server_app.web_app.add_handlers(".*$", handlers)
