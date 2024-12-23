import datetime

import pyzbar.pyzbar as pyzbar
# 이거 돌릴라면
# https://www.microsoft.com/ko-KR/download/details.aspx?id=40784
# 이거 깔아야함 ( visual c++ )
import winsound

import cv2
import threading
import time
import queue
import json

from DB.Database import Database
from DB.DatabaseConfig import *

data_list = []
used_codes = []
new_id = ''

cnt = 0
date = datetime.datetime.today().strftime("%Y%m%d")
# # 데이터 파일 읽어오기
try:
    f = open(f"{date}_data.json", "r")
    data_list = json.load(f)
except:
    with open(f"{date}_data.json", 'w') as f:
        json.dump(data_list, f, indent=4)
        print("=="*10,date,"_입실 데이터 파일 생성","=="*10)
else:
    f.close()

# DataBase
db = Database(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
# DB 연결
db.connect()

def start_camera(q, stop_event):
    cnt = 0
    cap = cv2.VideoCapture(0)  # 캠 시작
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 캠에서 바코드 인식
        barcode_data = pyzbar.decode(frame)
        if barcode_data :
            q.put(barcode_data)
            # x, y, w, h = barcode_data[0].rect

            # 이미지 인식 네모( 빨간색 네모 )
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            play_sound()
            time.sleep(1)
        cv2.imshow("Camera", frame)
        # keyboard 입력값 ( Q : 종료 , S : 이미지 저장 )
        key = cv2.waitKey(1)
        if key == ord('q'):
            stop_event.set()
            break
        elif key == ord('s'):
            cnt += 1
            cv2.imwrite('c_%03d.jpg' % cnt, frame)

    cap.release()
    cv2.destroyAllWindows()

def perform_task(q, stop_event, facility):
    while not stop_event.is_set():
        if not q.empty():
            barcode_data = q.get()
            # 바코드 내용
            barcode_text = barcode_data[0].data.decode("utf-8")
            # 바코드 타입 ( QR , Bar )
            barcode_type = barcode_data[0].type

            # 금일 입실 데이터 확인
            file = open(f"{date}_data.json", "w", encoding="utf8")
            check = [item for item in data_list if barcode_text in item]
            print("=="*20)
            print("입실데이터를 확인합니다....")
            print("접속한 User: ",barcode_text)
            if check:
                print("입실 데이터가 존재합니다.", check)
                print("퇴실처리 되었습니다. \n퇴실시간: ", datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))
                # 기존데이터 삭제
                rebuilding = [item for item in data_list if barcode_text not in item]
                json.dump(rebuilding, file)
                data_list.remove(check[0])
                file.close()
                db.update_checkout(check[0].get(barcode_text))
            else :
                print("입실데이터가 존재하지 않습니다.")
                print("=="*20)

                # 쿼리문 실행
                data, result = db.comparison(barcode_text, facility)
                if result == "reservation" :
                    new_id = db.insertDBReservation(data)
                    print("선택된 데이터 : ",result, "\n선택된 ID: ",data.get("reservation_id"))
                elif result == "enrollment" :
                    new_id = db.insertDBEnrollment(data)
                    print("선택된 데이터 : ",result, "\n선택된 ID : ",data.get("enrollment_id"))
                else :
                    new_id = None

                if new_id == None:
                    print("출석 데이터가 없습니다.")
                else :
                    # 데이터 추가
                    data = {barcode_text: new_id, date:datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")}
                    data_list.append(data)
                    json.dump(data_list, file)
                    file.close()

    print("프로그램 종료...")

def play_sound():
    sound_file = "C:/Users/Administrator/Desktop/Green_Project/QR_attendance/qrbarcode_beep1.wav"
    winsound.PlaySound(sound_file, winsound.SND_FILENAME)

def main(facility):
    q = queue.Queue()
    stop_event = threading.Event()

    # 캠 스레드
    camera_thread = threading.Thread(target=start_camera, args=(q, stop_event), daemon=True)
    camera_thread.start()

    # 바코드 처리 스레드
    task_thread = threading.Thread(target=perform_task, args=(q, stop_event,facility), daemon=True)
    task_thread.start()

    # 프로그램 종료 대기
    camera_thread.join()
    task_thread.join()

if __name__ == "__main__":
    sql = "select facility_id, facility_name from facility"
    facilityList = db.select_all(sql)
    print()
    print("Load Facility...")
    for idx, i in enumerate(facilityList) :
        print(f"{i['facility_name']} : {idx+1}")
    try:
        print()
        sc = input('QR 스캐너를 설치 할 시설을 선택해주세요(숫자입력) : ')
        facility = facilityList[int(sc)-1]['facility_id']
        print("\n선택된 시설정보 : ", facilityList[int(sc)-1]['facility_name'])
        main(facility)
    except :
        print("에러 발생, 프로그램을 종료합니다.")


# 카메라 QR 인식 : 1초에 한번
# 완료인데 카메라 너무 끊긴다. 어쩔수없다 최선의 방법으로 스레드 분할까지 했다;

# checkout point : 퇴실시간 이후 찍으면 체크아웃 / 두번 찍으면 퇴실? ( 시간 개념으로 잡다가 진짜 죽어 )
# 두번째 인식할수있는 데이터 셋을 만들어야함 ( 현 날짜기준으로 파일을 만들고 거기서 인식할수있게끔 만들면 될듯 //// 20241120 = [id1, id2, id3])
# 이것도 완료

# 둘 이상의 데이터가 있을 경우를 대비하여 아이디 값을 먼저 찾고, 있으면 출근, 없으면 퇴근 후 파일의 id 데이터 삭제
# 이것도 완료

# DB 순서 수정 해당 날짜의 앞에서부터 나오게 끔 ( 근데 오전/오후 두개인데 오후만 출근할 경우 고려 )
# 일단 완료 ( 현재 시간과 가까운것을 불러오게 끔 변경 했음 ) ( 테스트 완료 )
# 시간이 붙어 있을 때, 퇴실은 어케함? 막어? 막어 reservation 수정해야함.

# 지각 : 출근시간부터 + 10분까지 봐줌
# 이것도 완료 ( 테스트 완료 )

# 결석 : 50% 초과하고 찍으면 결석

# 시설이 인식되게끔 바꿔야 해
# 이것도 완료

# 두 가지 ( 예약, 수강 ) 데이터를 들고올 때는?

