import cv2
import pyzbar.pyzbar as pyzbar
from playsound import playsound, PlaysoundException

used_codes = []
data_list = []

cnt = 0

try:
    f = open("qrbarcode_data.txt", "r", encoding="utf8")
    data_list = f.readlines()
    print(data_list)
except FileNotFoundError:
    pass
else:
    f.close()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

for i in data_list:
    used_codes.append(i.rstrip('\n'))

while True:
    success, frame = cap.read()

    for code in pyzbar.decode(frame):
        my_code = code.data.decode('utf-8')
        print(code)
        if my_code not in used_codes:
            print("인식 성공 : ", my_code)
            try:
                playsound("C:/Users/Administrator/Desktop/Green_Project/QR_attendance/qrbarcode_beep.wav")
            except PlaysoundException as e:
                print(f"Error playing sound: {e}")
            used_codes.append(my_code)

            f2 = open("qrbarcode_data.txt", "a", encoding="utf8")
            f2.write(my_code+'\n')
            f2.close()
        elif my_code in used_codes:
            print("이미 인식된 코드 입니다.!!!")
            try:
                playsound("C:/Users/Administrator/Desktop/Green_Project/QR_attendance/qrbarcode_beep.wav")
            except PlaysoundException as e:
                print(f"Error playing sound: {e}")
        else:
            pass

    cv2.imshow('QRcode Barcode Scan', frame)

    # keyboard 입력값 ( Q : 종료 , S : 이미지 저장 )
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        cnt += 1
        cv2.imwrite('c_%03d.jpg' % cnt, frame)

