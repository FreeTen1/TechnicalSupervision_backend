from datetime import datetime
from os import path, popen
from configparser import ConfigParser

CONFIG_INI = "settings.ini"
CONFIG_PY = "config.py"
FLASK_RESTFUL_PY = "main_api.py"
GITIGNORE = '.gitignore'
START = 'start.sh'
README = 'README.md'
ENGINE = 'my_engine.py'
MODELS = 'models.py'

if not path.isfile(CONFIG_INI):
    db = input("Введите БД с которой будете работать: ")
    user = input("Введите пользователя phpmyadmin: ")
    password = input("Введите пароль от phpmyadmin: ")
else:
    from config import MYSQL
    db = MYSQL['database']
    user = MYSQL['user']
    password = MYSQL['password']


package_list = list()
not_enough_package = False
try:
    import flask
except:
    not_enough_package = True
    package_list.append('flask')

try:
    import flask_restful
except:
    not_enough_package = True
    package_list.append('flask_restful')

try:
    import mysql
except:
    not_enough_package = True
    package_list.append('mysql-connector')

if not_enough_package:
    print("Python doesn't have enough packages\nPlease run command", "'pip3 install", ' '.join(package_list) + "'")



def base_configurate_project():
    config_with_global = ConfigParser()
    if not path.isfile(CONFIG_INI):
        config_with_global.add_section('API')
        config_with_global.set('API', 'host', 'localhost')
        config_with_global.set('API', 'port', '5000')
        config_with_global.set('API', 'debug', 'False')
        config_with_global.set('API', 'build', 'False')

        config_with_global.add_section('MySQL')
        config_with_global.set('MySQL', 'host', 'localhost')
        config_with_global.set('MySQL', 'database', db if db else 'database')
        config_with_global.set('MySQL', 'user', user if user else 'user')
        config_with_global.set('MySQL', 'password', password if password else 'password')
        
        config_with_global.add_section('SECRET_KEY')
        config_with_global.set('SECRET_KEY', 'key', popen("uuidgen").read())
        
        with open(CONFIG_INI, 'w') as config_file:
            config_with_global.write(config_file)
    
    if not path.isfile(CONFIG_PY):
        with open(CONFIG_PY, 'w') as config_file:
            config_file.writelines(
                [
                    "from configparser import ConfigParser\n",
                    "config_with_global = ConfigParser()\n",
                    f"config_with_global.read('{CONFIG_INI}')\n",
                    "\n",
                    "API = config_with_global['API']\n",
                    "MYSQL = config_with_global['MySQL']\n"
                ]
            )
    
    if not path.isfile(GITIGNORE):
        with open(GITIGNORE, 'w') as gitignore_file:
            gitignore_file.writelines(
                [
                    "__pycache__\n",
                    "settings.ini\n",
                    "venv\n",
                    "stop_stomp.sh\n"
                ]
            )

    if not path.isfile(START):
        with open(START, 'w') as bash_start:
            my_str = """
DIRNAME=`dirname $0`
pid_name=`uuidgen`
if [ -z $1 ]; then
    echo 'not file_name'
else
    python_file=$1
    stop_file_name='stop_stomp.sh'
    PY3=`which python3`
    sudo start-stop-daemon -S -b -x $PY3 -d $DIRNAME -m -v -p /run/$pid_name.pid -- ./$python_file
    echo -e sudo start-stop-daemon -K -p /run/`echo $pid_name`.pid '\\n'sudo rm `echo $stop_file_name` '\\n'sudo rm /run/$pid_name.pid > $stop_file_name
fi
"""
            bash_start.write(my_str)

    if not path.isfile(README):
        with open(README, 'w') as readme:
            readme.writelines(
                [
                    ""
                ]
            )
    
    if not path.isfile(FLASK_RESTFUL_PY):
        with open(FLASK_RESTFUL_PY, 'w') as config_file:
            config_file.write(
                "from flask import Flask, Response, json\n"
                "from flask_restful import Api, Resource, reqparse\n"
                "from config import API\n"
                "from flask.wrappers import Request\n"
                "\n"
                "\n"
                "class AnyJsonRequest(Request):\n"
                "    def on_json_loading_failed(self, e):\n"
                "        if e is not None:\n"
                "            return super().on_json_loading_failed(e)\n"
                "\n"
                "\n"
                "app = Flask(__name__)\n"
                "api = Api(app, prefix='')\n"
                "app.request_class = AnyJsonRequest\n"
                "\n"
                "\n"
                "class _Resource(Resource):\n"
                "    parser = reqparse.RequestParser(trim=True)\n"
                "    #parser.add_argument('parser', type=str, default=False, required=True, choices=('M', 'F'), help='Bad choice: {error_msg}')\n"
                "\n"
                "    def return_json(self, body, status):\n"
                "        return Response(json.dumps(body, ensure_ascii=False), mimetype='application/json', status=status)\n"
                "\n"
                "    def return_status(self, status):\n"
                "        return Response(status=status)\n"
                "\n"
                "class _Class(_Resource):\n"
                "\n"
                "    def get(self):\n"
                "        args: dict = self.parser.parse_args()\n"
                "        return self.return_status(200)\n"
                "\n"
                "api.add_resource(_Class, '/class')\n"
                "\n"
                "if __name__ == '__main__':\n"
                "    app.run(host= API.get('host'), port= API.getint('port'), debug= API.getboolean('debug'))"
            )

    if not path.isfile(ENGINE):
        with open(ENGINE, 'w') as my_engine:
            my_str = """
from config import MYSQL
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import Session


engine = create_engine(f"mysql+mysqlconnector://{MYSQL['user']}:{MYSQL['password']}@{MYSQL['host']}/{MYSQL['database']}", encoding='utf8')
my_session = sessionmaker(bind=engine)
my_metadata = MetaData(bind=engine)


@contextmanager
def session_scope():
    session: Session = my_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

"""
            my_engine.write(my_str)

    if True:
        with open(MODELS, 'w') as models:
            my_str = ""
            if user and password and db:
                my_str += popen(f"sqlacodegen mysql+mysqlconnector://{user}:{password}@localhost/{db}").read().replace("# coding: utf-8", f"# update date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            else:
                my_str += '# Используйте команду "sqlacodegen mysql+mysqlconnector://{user}:{password}@localhost/{db_name}" для генерации моделей таблицы'
            models.write(my_str)


if __name__ == '__main__':
    base_configurate_project()
