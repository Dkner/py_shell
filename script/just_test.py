#coding=utf-8
import time
import datetime

birthday = '19931106'
created_at = '2015-11-06 16:24:42'

today_date = datetime.datetime.today()
birth_year = 0
if not birthday:
    birth_status = 0
else:
    this_year_birth_date = datetime.datetime.strptime(birthday, '%Y%m%d')
    this_year_birth_date = this_year_birth_date.replace(year=today_date.year)
    if birthday[4:] == datetime.datetime.today().strftime("%m%d"):
        birth_status = 1
        birth_year = today_date.year - int(birthday[:4])
    elif today_date > this_year_birth_date and \
                            today_date - this_year_birth_date <= datetime.timedelta(days=7):
        birth_status = 2
    else:
        birth_status = 0
# 2.周年庆
anniversary_year = 0
if not created_at:
    anniversary_status = 0
else:
    this_year_anniversary_date = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    this_year_anniversary_date = this_year_anniversary_date.replace(year=today_date.year, hour=0, minute=0, second=0)
    if this_year_anniversary_date.strftime('%m%d') == today_date.strftime("%m%d"):
        anniversary_status = 1
        anniversary_year = today_date.year - datetime.datetime.strptime(created_at,
                                                                        "%Y-%m-%d %H:%M:%S").year
    elif today_date > this_year_anniversary_date and \
                            today_date - this_year_anniversary_date <= datetime.timedelta(days=7):
        anniversary_status = 2
    else:
        anniversary_status = 0

print(birth_status, anniversary_status)
print(birth_year, anniversary_year)
print(int(86400 - (datetime.datetime.now() - datetime.datetime.today().replace(hour=0, minute=0, second=0)).total_seconds()))