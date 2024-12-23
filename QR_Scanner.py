import pyzbar.pyzbar as pyzbar
import cv2
from playsound import playsound
import winsound
from DB.Database import Database
from DB.DatabaseConfig import *
import time

# DataBase
db = Database(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
# DB 연결
db.connect()

# 비디오 캡쳐
cap = cv2.VideoCapture(0)

i = 0
while(cap.isOpened()):
  ret, img = cap.read()

  # 캠 인식 안되면 종료
  if not ret:
    continue

  # greyscale로 이미지 변환 및 디코딩
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  decoded = pyzbar.decode(gray)

  # for d in decoded:
  if decoded :
    d = decoded[0]
    print("dd ",d)
    x, y, w, h = d.rect

    # 바코드 내용
    barcode_data = d.data.decode("utf-8")
    # 바코드 타입 ( QR , Bar )
    barcode_type = d.type

    # 이미지 인식 네모( 빨간색 네모 )
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)


    # 인식된 내용 , 타입을 캠 내에 출력 ( 안쓸 꺼야 )
    # text = '%s (%s)' % (barcode_data, barcode_type)
    # cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    # 삑 ( 살짝 렉 걸리는 거 같은데 )
    sound_file = "C:/Users/Administrator/Desktop/Green_Project/QR_attendance/qrbarcode_beep1.wav"
    winsound.PlaySound(sound_file, winsound.SND_FILENAME)
    time.sleep(1)

    # 입력받은 데이터로
    # reservationdata, enrolldata = db.comparison(barcode_data)
    # print("reservation : ", reservationdata)
    # print("enrollment : ", enrolldata)
    # if reservationdata :
    #   db.insertDB(reservationdata)
    # elif enrolldata :
    #   db.insertDB(enrolldata)

    # 3초에 한번 인식
    # time.sleep(1)


  # 캠 화면 보여주기
  cv2.imshow('img', img)


  # keyboard 입력값 ( Q : 종료 , S : 이미지 저장 )
  key = cv2.waitKey(1)
  if key == ord('q'):
    break
  elif key == ord('s'):
    i += 1
    cv2.imwrite('c_%03d.jpg' % i, img)

cap.release()
cv2.destroyAllWindows()


def play_sound():
  sound_file = "C:/Users/Administrator/Desktop/Green_Project/QR_attendance/qrbarcode_beep1.wav"
  winsound.PlaySound(sound_file, winsound.SND_FILENAME)


# 카메라 QR 인식 : 3초에 한번
# 완료인데 카메라 너무 끊긴다.

# checkout point : 퇴실시간 이후 찍으면 체크아웃 / 두번 찍으면 퇴실? ( 시간 개념으로 잡다가 진짜 죽어 )
# 두번째 인식할수있는 데이터 셋을 만들어야함 ( 현 날짜기준으로 파일을 만들고 거기서 인식할수있게끔 만들면 될듯 //// 20241120 = [id1, id2, id3])
# 둘 이상의 데이터가 있을 경우를 대비하여 아이디 값을 먼저 찾고, 있으면 출근, 없으면 퇴근 후 파일의 id 데이터 삭제

# DB 순서 수정 해당 날짜의 앞에서부터 나오게 끔 ( 근데 오전/오후 두개인데 오후만 출근할 경우 고려 )

# 지각 : 출근시간부터 + 10분까지 봐줌

# 결석 : 50% 초과하고 찍으면 결석

#

