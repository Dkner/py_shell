from configparser import ConfigParser
cfg = ConfigParser()
cfg.read('../../config/config.ini')
cfg.sections()
print(cfg.get('installation','library'))
print(cfg.getboolean('debug','log_errors'))