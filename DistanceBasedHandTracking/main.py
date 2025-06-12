import cv2
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule as htm
import ArduinoConnection as ac

arduino = ac.manoArduino(puerto='COM4', baudaje=115200)
pTime = time.time()

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

tracker = htm.handDetector(max_num_hands=2,
               min_detection_confidence=0.8,
               min_tracking_confidence=0.8)

arduino.readArduino()

refPoints = (0,5)
handJoints = [(4,17),(5,8),(9,12),(13,16),(17,20)]
refMargins =(1.0,0.85,0.9,0.85,0.75)
#stepValues = [0] * 5

# Esperamos el reinicio del arduino
while (time.time()-pTime < 3):
    pass

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue
    img = cv2.flip(img,1)

    success = tracker.findHands(img)
    #handedness = tracker.findHandedness(img)
    #print(handedness)
    refDist = tracker.findDistance(0,refPoints[0],refPoints[1],img,True)
    #print(refDist)
    # Comando para mover todos los motores
    string = "m"
    for index, joint in enumerate(handJoints):
        dist1 = tracker.findDistance(0,joint[0],joint[1],img,False)
        #print(dist1)
        val = int(np.interp(dist1,[refDist/3, refDist*refMargins[index]], [180,0]))
        string = string + " " + str(val)
    print(string)
    value = arduino.writeArduino(string + "\n")
    arduino.readArduino()

    a,_ = tracker.findPosition(img,draw=True)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}',
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

    cv2.imshow("Image",img)

    if cv2.waitKey(5) & 0xFF == 27:
        break
    if cv2.getWindowProperty('Image',0) < 0:
        break

cap.release()
cv2.destroyAllWindows()