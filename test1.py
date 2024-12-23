import json
import datetime

from DB.Database import Database
from DB.DatabaseConfig import *

data_list = []

# DataBase
db = Database(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
# DB 연결
db.connect()
date = datetime.datetime.today().strftime("%Y%m%d")

# file=open(f"{date}_data.json","r")
# data_list = json.load(file)
# file.close()
# print("처음 불러줄거 ", data_list)
#
# user_id = 'user_id'
# file = open(f"{date}_data.json", "w", encoding="utf8")
# check = [item for item in data_list if user_id in item]
#
# print("중간 check", check)
# if check:
#     rebuilding = [item for item in data_list if user_id not in item]
#     json.dump(rebuilding, file)
# else :
#     data = {user_id : 'attendance_id'}
#     data_list.append(data)
#     json.dump(data_list, file)
# # data = {'user_id' : 'attendance_id'},
# # json.dump(data, file)
# file.close()
#
# file=open(f"{date}_data.json","r")
# data_list = json.load(file)
# file.close()
# print("새로운거",data_list)


# for item in content:
#     if 'user_id' in item:
#         print("dsadsa")


date = datetime.datetime.today().strftime("%Y-%m-%d")
now = datetime.datetime.now()
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

facility_id = "FC_1733382577187"
user_id = "muamjo"
reservationSql = '''
        select u.user_id, r.reservation_id, r.reservation_start, r.reservation_end , f.facility_name, f.facility_id from user u 
		join reservation r on r.user_id = u.user_id
		join court c on c.court_id = r.court_id
        join facility f on c.facility_id = f.facility_id
        where  r.user_id = '{}' and date(r.reservation_start) = '{}';
        '''.format(user_id, date)
enrollSql = '''
        select u.user_id, f.facility_name , e.enrollment_id, cd.class_id, cd.class_date, c.start_time, c.end_time, class_name from enrollment e
        join user u on u.user_id = e.user_id
        join class c on e.class_id = c.class_id
        join class_detail cd on c.class_id = cd.class_id and cd.class_date = '{}'
        join facility f on f.facility_id = c.facility_id and f.facility_id = '{}'
        where e.user_id = '{}';
        '''.format(date, facility_id, user_id)

# reservation filter
reservation_list = db.select_all(reservationSql)
if len(reservation_list) > 1:
    reservation_data = min(reservation_list, key=lambda x: abs(x['reservation_start'] - now))
elif not reservation_list :
    reservation_data = None
else :
    reservation_data = reservation_list[0]
print('reservation_list', reservation_list)
print('reservation_data', reservation_data)

# enrollment filter
enrollment_list = db.select_all(enrollSql)
if len(enrollment_list) > 1:
    enrollment_data = min(enrollment_list, key=lambda x: midnight + enrollment_data['start_time'] - now)
elif not enrollment_list:
    enrollment_data = None
else:
    enrollment_data = enrollment_list[0]
print('enrollment_list', enrollment_list)
print('enrollment_data', enrollment_data)
