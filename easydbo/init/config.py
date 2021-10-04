import configparser
from easydbo.init.file import File

class ConfigGetter(File):
    def __init__(self):
        self.filename = 'easydbo.cfg'

    def get(self):
        path = self.find(self.filename)
        # Load config file
        cfg = configparser.ConfigParser()
        cfg.read(path)
        # Set
        cfgs = {
            'database': dict(cfg['database'].items()),
            'excel': dict(cfg['excel'].items()),
        }
        return cfgs
