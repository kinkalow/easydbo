import configparser
from easydbo.init.file import File

class ConfigLoader(File):
    def __init__(self):
        self.filename = 'easydbo.cfg'
        self.cfg = self._load()

    def _load(self):
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

    def get(self):
        return self.cfg
