import cv2
import mediapipe as mp
import numpy as np
import time


class handDetector():
    def __init__(self,
               static_image_mode=False,
               max_num_hands=2,
               min_detection_confidence=0.5,
               min_tracking_confidence=0.5):
        """
        Constructor de clase. Construye el modelo detector con los parámetros especificados.
        """
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(self.static_image_mode,
                                        self.max_num_hands, 1,
                                        self.min_detection_confidence,
                                        self.min_tracking_confidence)

    def findHands(self, img, draw = True):
        success = False
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB.flags.writeable = False
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            success = True
            if draw:
                for hand_landmarks in self.results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(img, hand_landmarks,
                                                   self.mp_hands.HAND_CONNECTIONS,
                                                   self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                                   self.mp_drawing_styles.get_default_hand_connections_style())

        return success
    
    def findHandedness(self, img, draw = True):
        output = []
        
        if self.results.multi_hand_landmarks:
            for index, hand in enumerate(self.results.multi_handedness):
                #print(hand.classification)
                label = hand.classification[0].label
                score = round(hand.classification[0].score, 2)
                
                output.append(label)

                if draw:
                    height, width, _ = img.shape
                    wrist_normalized_coords = self.results.multi_hand_landmarks[index].landmark[self.mp_hands.HandLandmark.WRIST]
                    wrist_coords = tuple(np.multiply(
                                                        [wrist_normalized_coords.x,wrist_normalized_coords.y],
                                                        [width+10 ,height+40]
                                                    ).astype(int)
                                        )
                    cv2.putText(img, f'{label} - {score}', wrist_coords, cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2,cv2.LINE_AA)
    
        return output
    
    def findPosition(self, img, handNo=0, draw=False):
        self.lmList = []
        xList = []
        yList = []
        boundingBox = []

        if self.results.multi_hand_landmarks:
            for id, landmark in enumerate(self.results.multi_hand_landmarks[handNo].landmark):
                #print(id, landmark)
                h, w, _ = img.shape
                x, y = int(landmark.x*w), int(landmark.y*h)
                xList.append(x)
                yList.append(y)
                self.lmList.append([id, x, y])
                if draw:
                    if id == 0:
                        cv2.circle(img,(x,y),15,(255,0,255),cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boundingBox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (boundingBox[0]-20,boundingBox[1]-20),
                              (boundingBox[2]+20,boundingBox[3]+20), (0,255,0),2)
        
        return self.lmList, boundingBox

    def detectCompleteHand(self, handNo=0, img =[], draw = True):
        success = False
        if self.results.multi_hand_landmarks:
            print(self.results.multi_hand_landmarks[handNo].landmark)
            print(len(self.results.multi_hand_landmarks[handNo].landmark))
        return success
    
    def findDistance(self,handNo,id1,id2, img, draw=True):
        distance = 0

        if self.results.multi_hand_landmarks:
            lm1 = self.results.multi_hand_landmarks[handNo].landmark[id1]
            lm2 = self.results.multi_hand_landmarks[handNo].landmark[id2]
            p1 = np.array([lm1.x, lm1.y, lm1.z])
            p2 = np.array([lm2.x, lm2.y, lm2.z])

            squared_dist = np.sum((p1-p2)**2, axis=0)
            distance = np.sqrt(squared_dist)

            if draw:
                h, w, _ = img.shape
                cv2.line(img,(int(lm1.x*w),int(lm1.y*h)),
                         (int(lm2.x*w),int(lm2.y*h)),(255,0,255),3)
        
        return distance
    

def main():
    wCam, hCam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    detector = handDetector()

    pTime = 0.0
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        img = cv2.flip(img,1)

        success = detector.findHands(img)
        
        #a = detector.detectCompleteHand()
        #print(a)

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


if __name__ == "__main__":
    main()