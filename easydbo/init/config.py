import configparser
from easydbo.init.file import File
from easydbo.util.dictionary import NamedDict
from easydbo.exception import EASYDBO_FATAL_ERROR

_default = {
    'easydbo': {
        'verbose': 0
    },
    'database': {
        'database': '',
        'host': '',
        'password': '',
        'port': '',
        'user': '',
    },
    'output': {
        'format': '',
    },
    'table_window': {
        'enable_all_save': True,
        'enable_all_print': True,
        'enable_all_greprun': True,
        'enable_selected_copypaste': True,
        'enable_selected_save': True,
        'enable_selected_print': True,
        'enable_rightclick_cell_copypaste': True,
        'enable_rightclick_cell_print': True,
        'enable_rightclick_row_copypaste': True,
        'enable_rightclick_row_print': True,
        'enable_rightclick_selected_copypaste': True,
        'enable_rightclick_selected_print': True,
        'enable_rightclick_selected_save': True,
        'enable_rightclick_all_print': True,
        'enable_rightclick_all_save': True,
    },
}

class ConfigLoader(File):
    def __init__(self):
        self.filename = 'easydbo.cfg'
        self.cfg = self._load()

    def _load(self):
        path = self.find(self.filename)
        # Load config file
        cfg = configparser.ConfigParser()
        cfg.read(path)
        # Updates
        cfgs = {}
        for section, dict_ in _default.items():
            cfgs[section] = {}
            for key, default_value in dict_.items():
                type_ = type(_default[section][key])
                try:
                    if type_ is bool:
                        value = cfg.getboolean(section, key)
                    elif type_ is int:
                        value = cfg.getint(section, key)
                    elif type_ is str:
                        value = cfg[section][key]
                    else:
                        raise EASYDBO_FATAL_ERROR(f'class ConfigLoader: value={cfg[section][key]}, type={type_}')
                    cfgs[section][key] = value
                except configparser.NoOptionError:
                    cfgs[section][key] = default_value
        cfgs = NamedDict({k: NamedDict(v) for k, v in cfgs.items()})
        return cfgs

    def get(self):
        return self.cfg
