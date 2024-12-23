import datetime
from datetime import timedelta

import pymysql
import pymysql.cursors
import logging

class Database :

    def __init__(self, host, user, password, db_name, charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.charset = charset
        self.db_name = db_name
        self.conn = None

    # DB 연결
    def connect(self):
        if self.conn != None :
            return
        try:
            self.conn = pymysql.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                db = self.db_name,
                charset = self.charset
            )
            print("DB connected...")
            return self.conn
        except:
            print("Error DB connect")
            return None

    # DB 종료
    def close(self):
        if self.conn is None:
            return

        if not self.conn.open:
            self.conn = None
            return
        self.conn.close()
        self.conn = None

    # insert
    def execute(self, sql, param):
        last_row_id = -1
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, param)
            self.conn.commit()
            logging.debug("execute last_row_id: %d", last_row_id)
        except Exception as ex:
            logging.error(ex)
        finally:
            return last_row_id

    # SELECT 구문 실행 후, 데이터 호출 (한개)
    def select_one(self, sql):
        result = None
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
        except Exception as ex:
            logging.error(ex)
        finally:
            return result

    # SELECT 구문 실행 후, 데이터 호출 (전부)
    def select_all(self, sql):
        result = None
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
        except Exception as ex:
            logging.error(ex)
        finally:
            return result

    # 검색 쿼리
    def make_query(self, column, table):
        sql = "select {} from {}".format(column, table)
        return sql

    # 타입 비교
    def comparison(self, user_id, facility_id):
        date = datetime.datetime.today().strftime("%Y-%m-%d")
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # date = "2024-11-28"
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
        reservation_list = self.select_all(reservationSql)
        if len(reservation_list) > 1:
            reservation_data = min(reservation_list, key=lambda x: abs(x['reservation_start'] - now))
        elif not reservation_list :
            reservation_data = None
        else :
            reservation_data = reservation_list[0]

        # enrollment filter
        enrollment_list = self.select_all(enrollSql)
        if len(enrollment_list) > 1:
            enrollment_data = min(enrollment_list, key=lambda x: midnight + enrollment_data['start_time'] - now)
        elif not enrollment_list:
            enrollment_data = None
        else :
            enrollment_data = enrollment_list[0]

        print("enrollment_list", enrollment_list)
        print("reservation_list", reservation_list)

        if enrollment_data is not None:
            enroll = abs((midnight + enrollment_data.get('start_time')) - now)
            enroll_time = enrollment_data["end_time"] - enrollment_data["start_time"]
            print()
            print("===========강의============ \n",(midnight + enrollment_data.get('start_time')),"(예약시간)" ," - ", now,"(현재시간)", "\n", enroll,"(시간차이)")
            print()
        else :
            enroll = datetime.timedelta(hours=100)
            enroll_time = datetime.timedelta(hours=1)

        if reservation_data is not None:
            reservation = abs(reservation_data.get('reservation_start') - now)
            reservation_time = reservation_data['reservation_end'] - reservation_data['reservation_start']
            print()
            print("===========시설예약============ \n", (reservation_data.get('reservation_start')),"(예약시간)", "-", now,"(현재시간)" ,"\n", reservation,"(시간차이)" )
            print()
        else :
            reservation = datetime.timedelta(hours=100)
            reservation_time = datetime.timedelta(hours=1)

        if enroll < reservation and enroll < enroll_time:
            result = "enrollment"
            return enrollment_data, result
        elif enroll > reservation and reservation < reservation_time :
            result = "reservation"
            return reservation_data, result
        else :
            result = None
            return None , result

    # insert DB
    def insertDBReservation(self, data):
        date = datetime.datetime.today().strftime("%Y%m%d")
        attendancesql = self.make_query("*", "attendance")
        attendance = self.select_all(attendancesql)

        # 기존에 reservation_id가 있는지 확인
        reservation_check = [item for item in attendance if item.get('reservation_id') and data.get('reservation_id') in item.get('reservation_id')]

        if not reservation_check :
            # Attendence_id 생성
            # 오늘 날짜를 기준으로 001 ~ 시작
            today_attendance= [item for item in attendance if date in item['attendance_id']]
            id = "A_" + date + format(len(today_attendance) + 1, '03')

            # attendance_status Setting
            # 10분 늦으면 지각 처리
            status = "Present"
            if data["reservation_start"] + datetime.timedelta(minutes=10) < datetime.datetime.now():
                status = "Late"
            if(status == "Present"):
                print("입실 판정: 정상 입실")
            else:
                print("입실 판정: 지각 ")
            print()
            sql = '''
            insert into attendance(attendance_id, reservation_id, attendance_status, checkin_date)
            values(%s, %s, %s, %s)
            '''

            self.execute(sql,(id,data['reservation_id'],status, datetime.datetime.now()))
            return id
        else :
            print("이미 데이터가 있어요")

    # insert DB
    def insertDBEnrollment(self, data):
        date = datetime.datetime.today().strftime("%Y%m%d")
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        attendancesql = self.make_query("*", "attendance")
        attendance = self.select_all(attendancesql)

        # 기존에 enrollment_id가 있는지 확인
        enrollment_check = [item for item in attendance if item.get('enrollment_id') and data.get('enrollment_id') in item.get('enrollment_id') ]

        if not enrollment_check:
            # Attendence_id 생성
            # 오늘 날짜를 기준으로 001 ~ 시작
            today_attendance = [item for item in attendance if date in item['attendance_id']]
            id = "A_" + date + format(len(today_attendance) + 1, '03')

            # attendance_status Setting
            # 10분 늦으면 지각 처리
            status = "Present"
            if midnight + data.get("start_time") + datetime.timedelta(minutes=10) < datetime.datetime.now():
                status = "Late"

            print('attendence_id: ', id)
            print("status: ", status)

            sql = '''
                            insert into attendance(attendance_id,enrollment_id, attendance_status, checkin_date)
                            values(%s, %s, %s, %s)
                            '''
            print("데이터가 없어요")
            print("새로 추가할게요")
            self.execute(sql,(id,data.get('enrollment_id'),status, datetime.datetime.now()))
            return id
        else:
            print("이미 데이터가 있어요")

    def update_checkout(self,attendance_id):
        date = datetime.datetime.now()
        print("date", date)
        sql = "update attendance set checkout_date = %s where attendance_id = %s"
        self.execute(sql,(date, attendance_id))