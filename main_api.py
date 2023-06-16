from datetime import datetime, timedelta, timezone
from waitress import serve
from flask import Flask, Response, json, send_file
from flask_restful import Api, Resource, reqparse
from config import API, SECRET_KEY
from flask.wrappers import Request
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt,
                                get_jwt_identity, jwt_required,
                                set_access_cookies, unset_jwt_cookies)
from functions import add_supervision, authorization, change_supervision, delete_supervision, excel_load, get_lists, get_single_supervision, get_supervisions, supervisions_count_info, take_in_ks


class AnyJsonRequest(Request):
    def on_json_loading_failed(self, e):
        if e is not None:
            return super().on_json_loading_failed(e)


app = Flask(__name__)
app.request_class = AnyJsonRequest

app.config['PROPAGATE_EXCEPTIONS'] = True  # Нужно чтобы всегда были 401 ошибки если чего-то не хватает в авторизации
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
# Не очищает куки после закрытия браузера.
app.config["JWT_SESSION_COOKIE"] = False
# Позволяет отправлять запросы без проверки CSRF
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
# app.config["JWT_COOKIE_SECURE"] = True # Только через HTTPS соединение
app.config["JWT_SECRET_KEY"] = SECRET_KEY.get("key")
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

api = Api(app, prefix="")
jwt = JWTManager(app)


class _Resource(Resource):
    parser = reqparse.RequestParser(trim=True)
    # parser.add_argument('parser', type=str, default=False, required=True, choices=('M', 'F'), help='Bad choice: {error_msg}')

    def return_json(self, body, status):
        return Response(
            json.dumps(body, ensure_ascii=False),
            mimetype="application/json",
            status=status,
        )

    def return_status(self, status):
        return Response(status=status)


# @app.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()['exp']
#         now = datetime.utcnow()
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=5))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         return response


class TechnicalSupervisions(_Resource):
    """Работа с тех. надзорами"""
    # аргументы для добавления
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('datetime_start', type=str, required=True)
    parser.add_argument('datetime_end', type=str, required=True)
    parser.add_argument('day_type_id', type=int, required=True)
    parser.add_argument('station', type=str)
    parser.add_argument('department_responsible_id', type=int, required=True)
    parser.add_argument('department_distance', type=str)
    parser.add_argument('artist', type=str) # Добавится если такого ещё не было
    parser.add_argument('type_work', type=str)
    parser.add_argument('contractor_id', type=int)
    parser.add_argument('manufacturer_info', type=str)
    parser.add_argument('order_number', type=str)
    parser.add_argument('note', type=str)
    parser.add_argument('status_ks_id', type=int)
    parser.add_argument('comment', type=str)
    parser.add_argument('paid_status_id', type=int)
    parser.add_argument('amount', type=int)
    parser.add_argument('status_execution_id', type=int)

    # аргументы для получения
    parser_get = reqparse.RequestParser(trim=True)
    parser_get.add_argument('date_start', type=str)
    parser_get.add_argument('date_end', type=str)
    parser_get.add_argument('contractor_id', type=int)
    parser_get.add_argument('status_ks_id', type=int)
    parser_get.add_argument('status_execution_id', type=int)
    parser_get.add_argument('year', type=int)
    parser_get.add_argument('month', type=int)
    parser_get.add_argument('sort_key', type=str, choices=("id", 'datetime_start', 'datetime_end', 'station'))
    parser_get.add_argument('sort_by', type=str, choices=('ASC', 'DESC'), help='Неверный вид сортировки') # DESC - убывание, ASC - возрастание

    @jwt_required()
    def get(self, supervision_id=None):
        """
        - Вывод тех. надзоров. 
        - Если передан supervision_id - вывод всей информации по конкретному тех. надзору
        """
        if supervision_id:
            return self.return_json(*get_single_supervision(supervision_id))
        else:
            args: dict = self.parser_get.parse_args()
            return self.return_json(*get_supervisions(args))

    @jwt_required()
    def post(self):
        """Добавление нового тех. надзора"""
        args: dict = self.parser.parse_args()
        return self.return_json(*add_supervision(args))

    @jwt_required()
    def put(self, supervision_id):
        """изменение конкретного тех. надзора"""
        args: dict = self.parser.parse_args()
        return self.return_json(*change_supervision(supervision_id, args))

    @jwt_required()
    def delete(self, supervision_id):
        """изменение конкретного тех. надзора"""
        return self.return_json(*delete_supervision(supervision_id))


class Lists(_Resource):
    """Выпадающие списки"""

    @jwt_required()
    def get(self):
        return self.return_json(*get_lists())


class ExcelLoad(_Resource):
    """Выгрузка данных"""
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('supervision_ids', type=str, required=True)
    parser.add_argument('load_type', type=str, required=True, choices=('inside', 'outside'))

    @jwt_required()
    def get(self):
        """supervision_ids должен иметь вид supervision_ids=1,2,3,4,5"""
        args: dict = self.parser.parse_args()
        try:
            supervision_ids = list(map(int, args["supervision_ids"].split(",")))
        except ValueError as e:
            return self.return_json({"message": f"Ошибка! Невозможно преобразовать строку {str(e).split(' ')[-1]} в число."}, 400)

        return send_file(path_or_file=excel_load(supervision_ids, args["load_type"]), download_name='Выгрузка.xlsx', as_attachment=True)


class TakeInKs(_Resource):
    """Учесть в КС"""
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('take_in_ks_ids', action='append', type=int)
    parser.add_argument('not_take_in_ks_ids', action='append', type=int)

    @jwt_required()
    def put(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*take_in_ks(args["take_in_ks_ids"], args["not_take_in_ks_ids"]))
    

class SupervisionsCountInfo(_Resource):
    """Получить количественную информацию о тех. надзорах"""
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('year', type=int, required=True)

    @jwt_required()
    def get(self):
        args: dict = self.parser.parse_args()
        return self.return_json(*supervisions_count_info(args["year"]))


class Auth(_Resource):
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('login', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    
    @jwt_required()
    def get(self):
        return self.return_status(200)

    def post(self):
        args: dict = self.parser.parse_args()
        user, status = authorization(args["login"], args["password"])
        if status == 200:
            access_token = create_access_token(identity=user['login'], additional_claims=user)
            resp = self.return_json({"access_token": access_token}, 200)
            set_access_cookies(resp, access_token)
            return resp
        else:
            return self.return_json(user, status)
    
    @jwt_required()
    def delete(self):
        resp = self.return_status(200)
        unset_jwt_cookies(resp)
        return resp


build = "" if API.getboolean("build") else "/api"

api.add_resource(TechnicalSupervisions, f"{build}/supervisions", f"{build}/supervisions/<int:supervision_id>")
api.add_resource(Lists, f"{build}/lists")
api.add_resource(ExcelLoad, f"{build}/excel_load")
api.add_resource(TakeInKs, f"{build}/take_in_ks")
api.add_resource(SupervisionsCountInfo, f"{build}/supervisions_count_info")
api.add_resource(Auth, f"{build}/auth")


if __name__ == "__main__":
    if API.getboolean("debug"):
        app.run(host=API.get("host"),
                port=API.getint("port"),
                debug=API.getboolean("debug"))
    else:
        serve(app, port=API.getint("port"))

