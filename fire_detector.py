import cv2
import numpy as np
import smtplib
import playsound
import threading
import os

Alarm_Status = False
Email_Status = False
Fire_Reported = 0


def play_alarm_sound_function():  # turns the alarm sound on
    while True:
        playsound.playsound('Alarm Sound.mp3', True)


def send_mail_function():  # sends alert message as an email

    recipientEmail = ""   #Enter the email id of the receiver 
    recipientEmail = recipientEmail.lower()

    mailId = os.getenv('FOREST_USER')
    password = os.getenv('FOREST_PASS')
    print(mailId)
    print(password)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(mailId, password)
        server.sendmail(mailId, recipientEmail, "Warning A Fire Accident has been reported.")
        print("sent to {}".format(recipientEmail))
        server.close()
    except Exception as e:
        print(e)


video = cv2.VideoCapture("forest1.avi")  # takes the input video for processing.

while True:
    (grabbed, frame) = video.read()
    if not grabbed:
        break

    frame = cv2.resize(frame, (960, 540))  # resize the video frame

    blur = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)  # convert video from RGB to HSV

    lower = [18, 50, 50]
    upper = [35, 255, 255]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    mask = cv2.inRange(hsv, lower, upper)

    output = cv2.bitwise_and(frame, hsv, mask=mask)

    no_red = cv2.countNonZero(mask)  # total number of fire pixels

    if int(no_red) > 15000:
        Fire_Reported = Fire_Reported + 1

    cv2.imshow("output", output)

    if Fire_Reported >= 1:

        if not Alarm_Status:
            threading.Thread(target=play_alarm_sound_function).start()
            Alarm_Status = True

        if not Email_Status:
            threading.Thread(target=send_mail_function).start()
            Email_Status = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
video.release()
