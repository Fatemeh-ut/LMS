import datetime
from datetime import date, datetime


def age_gt(birth_date, num):
    date_format = "%Y-%m-%d"
    birth_date = datetime.strptime(birth_date, date_format).date()
    today = date.today()
    age = today.year - birth_date.year -((today.month, today.day) < (birth_date.month, birth_date.day))

    return age < num

def positive_number(num):
    num = int(num)
    return True if num >= 0 else False


def be_future(this_date):
    date_format = "%Y-%m-%d"
    this_date = datetime.strptime(this_date, date_format).date()
    today = date.today()
    return today.__lt__(this_date)
