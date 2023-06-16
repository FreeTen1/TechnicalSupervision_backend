from datetime import datetime


def general_filter(params: dict) -> dict:
    """функция которая превращает пустую строку в None.\n
    Например: 
    - было {"value1": "123", "value2": ""}
    - станет {"value1": "123", "value2": None}
    """
    return dict([(k, None if v == '' else v) for k, v in params.items()])


def compare_dates(date_start, date_end):
    """функция которая сравнивает две даты и возвращает True, если первая дата меньше или равна второй дате, и False в противном случае"""
    try:
        start = datetime.strptime(date_start, '%Y-%m-%d')
        end = datetime.strptime(date_end, '%Y-%m-%d')
        return start <= end
    except ValueError:
        return False


def hours_between_dates(datetime_start, datetime_end):
    date_format = '%Y-%m-%d %H:%M'
    datetime_start = datetime.strptime(datetime_start, date_format)
    datetime_end = datetime.strptime(datetime_end, date_format)
    delta = datetime_end - datetime_start
    hours = delta.total_seconds() / 3600
    return round(hours)