from datetime import datetime
from datetime import timedelta


class settings(object):
    days_of_the_week = [
        [
            'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday'
        ],
        ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    ]
    date_formats = ['%Y-%m-%d %H:%M', '%Y-%m-%d']
    year_suffix = 'y'
    month_suffix = 'm'
    week_suffix = 'w'
    day_suffix = 'd'
    hour_suffix = 'h'
    minute_suffix = 'i'
    second_suffix = 's'


def expand(date_text, date_format, datetime_format=None):
    date_format = _determine_date_format(
        date_format, datetime_format, date_text
    )
    return parse(date_text).strftime(date_format)


def _determine_date_format(date_format, datetime_format, date_text):
    if not datetime_format:
        return date_format
    if _check_begining_for_time(date_text, datetime_format):
        return datetime_format
    if _check_end_for_time(date_text):
        return datetime_format
    return date_format


def _check_begining_for_time(date_text, datetime_format):
    if date_text in ('n', 'ns', 'ni', 'nh'):
        return True
    if any((
        date_text.startswith(w) for w in (
            'now', 'next hour', 'next minute', 'next second'
        )
    )):
        return True
    for i in range(0, len(date_text)):
        if is_date(date_text, [datetime_format, '%H:%M']):
            return True
    return False


def _check_end_for_time(date_text):
    return any((
        date_text.endswith(e) for e in (
            settings.second_suffix,
            settings.minute_suffix,
            settings.hour_suffix
        )
    ))


def parse(date_text):
    now = datetime.now()
    parsed_date = now
    for i in range(len(date_text), 0, -1):
        date = date_text[:i]
        transformation = date_text[i:]
        parsed_date = parse_date(date)
        if parsed_date:
            return parse_transformation(transformation)(parsed_date)
    return parsed_date or parse_transformation(date_text)(now)


def parse_transformation(transformation_text):
    if not transformation_text:
        return lambda x: x
    transformation_text = transformation_text.lower()
    operation = _extract_operation(transformation_text)
    delta_int = _extract_delta(transformation_text)
    if transformation_text.endswith(settings.month_suffix):
        return _make_month_transformation(operation, delta_int)
    elif transformation_text.endswith(settings.year_suffix):
        return _make_year_transformation(operation, delta_int)
    elif transformation_text.endswith(settings.week_suffix):
        return _make_simple_transformation(operation, delta_int * 7, settings.day_suffix)
    return _make_simple_transformation(operation, delta_int, transformation_text)


def _extract_operation(transformation_text):
    def plus(s, c): return s + c

    def minus(s, c): return s - c

    if transformation_text.startswith('-'):
        return minus
    return plus  # addition is default


def _extract_delta(transformation_text):
    for substr in [
        transformation_text,
        transformation_text[1:],
        transformation_text[:-1],
        transformation_text[1:-1],
    ]:
        if substr.isdigit():
            delta = int(substr)
            return delta
    return 1


def _make_month_transformation(operation, delta_int):
    def transformation(some_datetime):
        years = delta_int / 12
        new_year = operation(some_datetime.year, years)
        months = delta_int % 12
        new_month = operation(some_datetime.month, months)
        if new_month > 12:
            new_month = new_month % 12
            new_year += 1
        if new_month < 1:
            new_month = 12 + new_month
            new_year -= 1
        return some_datetime.replace(year=int(new_year), month=int(new_month))
    return transformation


def _make_year_transformation(operation, delta_int):
    def transformation(some_datetime):
        year = operation(some_datetime.year, delta_int)
        return some_datetime.replace(year=year)
    return transformation


def _make_simple_transformation(operation, delta_int, transformation_text):
    delta = timedelta(days=delta_int)
    for suffix, parameter in (
        (settings.hour_suffix, 'hours'),
        (settings.minute_suffix, 'minutes'),
        (settings.second_suffix, 'seconds'),
    ):
        if transformation_text.endswith(suffix):
            delta = timedelta(**{parameter: delta_int})

    def transformation(some_datetime):
        return operation(some_datetime, delta)
    return transformation


def parse_date(date_text):
    date_text = date_text.lower()
    for parse in (
        _parse_now,
        _parse_next_year,
        _parse_next_month,
        _parse_next_day,
        _parse_next_hour,
        _parse_next_minute,
        _parse_next_second,
        _parse_next_week,
        _parse_day_of_the_week,
        _parse_full_date,
        _parse_hour,
    ):
        parsed_date = parse(date_text)
        if parsed_date:
            return parsed_date


def _parse_now(date_text):
    if date_text in ['now', 'today', 'n', 't']:
        return datetime.now()


def _parse_next_year(date_text):
    if date_text in ['next year', 'ny']:
        return datetime(datetime.now().year + 1, 1, 1, 0, 0)


def _parse_next_month(date_text):
    now = datetime.now()
    if date_text in ['next month', 'nm']:
        if now.month == 12:
            return parse_date('next year')
        else:
            return datetime(now.year, now.month + 1, 1, 0, 0)


def _parse_next_day(date_text):
    if date_text in ['next day', 'nd', 'tomorrow']:
        return (datetime.now() + timedelta(days=1)).replace(
            hour=0, minute=0, second=0
        )


def _parse_next_hour(date_text):
    if date_text in ['next hour', 'nh']:
        return (datetime.now() + timedelta(hours=1)).replace(
            minute=0, second=0
        )


def _parse_next_minute(date_text):
    if date_text in ['next minute', 'nm']:
        return (datetime.now() + timedelta(minutes=1)).replace(
            second=0
        )


def _parse_next_second(date_text):
    if date_text in ['next second', 'ns']:
        return datetime.now() + timedelta(seconds=1)


def _parse_next_week(date_text):
    now = datetime.now()
    if date_text in ['next week', 'nw']:
        midnight = now.replace(hour=0, minute=0, second=0)
        monday = midnight + timedelta(days=(7 - now.weekday()))
        return monday


def _parse_day_of_the_week(date_text):
    now = datetime.now()
    for days in settings.days_of_the_week:
        if date_text in days:
            index = days.index(date_text)
            midnight = now.replace(hour=0, minute=0, second=0)
            monday = midnight + timedelta(days=(7 - now.weekday()))
            return monday + timedelta(days=index)


def _parse_full_date(date_text):
    for date_format in settings.date_formats:
        try:
            return datetime.strptime(date_text, date_format)
        except ValueError:
            pass


def _parse_hour(date_text):
    now = datetime.now()
    if ':' not in date_text:
        return
    hour, minute = date_text.split(':')
    try:
        hour, minute = int(hour), int(minute)
    except ValueError:
        return
    proper_time = now.replace(hour=hour, minute=minute)
    if proper_time < now:
        proper_time += timedelta(days=1)
    return proper_time


def is_date(text, date_formats=None):
    date_formats = date_formats or settings.date_formats
    for date_format in date_formats:
        try:
            datetime.strptime(text, date_format)
            return True
        except ValueError:
            pass
    return False
