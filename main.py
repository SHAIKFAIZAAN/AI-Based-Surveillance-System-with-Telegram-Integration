import time
import cv2
from pyfirmata import Arduino, util
import face_recognition
import winsound
import requests

port = Arduino('COM3')
TOKEN = "7150869348:AAFbt6WepYxZd2e_NsGdU4MwYs0x6viAiW0"
warn = [False]
match_ = [False]

iter = util.Iterator(port)
iter.start()

servo = port.get_pin('d:9:s')
led = port.get_pin('d:12:o')
led1 = port.get_pin('d:11:o')

servo.write(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

known_faces = ["./assets/3.jpg"]
names = ['Faizaan']

known_faces_encodings = []

def beep():
    frequency = 2000  # Set Frequency To 2500 Hertz
    duration = 1500  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

def send_photo(chat_id = "5244701877"):
    file_opened = open("unkn.jpg", 'rb')
    params = {'chat_id': chat_id}
    files = {'photo': file_opened}
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    # "https://api.telegram.org/bot' + botToken + '/sendPhoto -F chat_id=' + chat_id + " -F photo=@" + imageFile"
    resp = requests.post(url, params, files=files)
    print(resp)

def Train(images = known_faces):
    for loc in images:
        img = face_recognition.load_image_file(loc)
        enc = face_recognition.face_encodings(img)[0]
        known_faces_encodings.append(enc)

def sendMessage(message):
    warn[0] = True
    chat_id = "5244701877"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) 

def detect_known_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        face_encoding = face_recognition.face_encodings(face_roi)
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        if True in matches:
            return True
        else:
            return False

def detect(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        print(True in matches)
        if True in matches:
            match_[0] = True
            led1.write(1)
            for i in range(len(matches)):
                if(matches[i] == True):
                    cv2.imwrite("unkn.jpg", frame) 
                    send_photo()
                    sendMessage(f"{names[i]} detected ...")
            beep()
            time.sleep(1)
            servo.write(180)
            time.sleep(5)
            servo.write(0)

        else:
            sendMessage("Unkown person detected..")
            cv2.imwrite("unkn.jpg", frame) 
            send_photo()
Train()

vid = cv2.VideoCapture(0)
i = 0
while(True): 
    print("warn ", warn)
    if(i == 10):
        i = 0
        warn[0] = False
        match_[0] = False
    if(warn[0]):
        if(match_[0]):
            led1.write(1)
        else:
            led.write(1)
        i += 1
        time.sleep(1)
        continue
    led.write(0)
    led1.write(0)
    ret, frame = vid.read()
    detect(frame) 
     