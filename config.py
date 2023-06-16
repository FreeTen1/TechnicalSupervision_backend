from configparser import ConfigParser
config_with_global = ConfigParser()
config_with_global.read('settings.ini')

API = config_with_global['API']
MYSQL = config_with_global['MySQL']
SECRET_KEY = config_with_global['SECRET_KEY']
