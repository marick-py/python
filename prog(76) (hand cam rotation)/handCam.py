from turtle import position
import mediapipe as mp
import numpy as np
from e2D import *
import cv2

mp_drawing, mp_drawing_styles, mp_hands = mp.solutions.drawing_utils, mp.solutions.drawing_styles, mp.solutions.hands

def get_hand_rotation(info):
    wrist, middle_finger_tip = info.multi_hand_landmarks[0].landmark[0], info.multi_hand_landmarks[0].landmark[12]
    mid_deep = (wrist.z + middle_finger_tip.z) / 2
    wrist, middle_finger_tip = V2(wrist.x, wrist.y), V2(middle_finger_tip.x, middle_finger_tip.y)
    return wrist.angle_to(middle_finger_tip) + 90, wrist.mid_point_to(middle_finger_tip), mid_deep

def main(camDefault=True):
    global handInfo, actionDone
    cam = cv2.VideoCapture((int(input("Camera Device:\n>>> ") if not camDefault else 2)))
    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.4) as hands:
        while cam.isOpened():
            success, image = cam.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            rotation, center, deep = 0, V2(0,0), 1
            right_deep = 0.1
            if results.multi_hand_landmarks:
                rotation, center, deep = get_hand_rotation(results)
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
            normal_image = image.copy()
            MIDDLE_SCREEN = (V2(info=image.shape[:2][::-1])/2)
            MIDDLE = (center * V2(info=image.shape[:2][::-1]))
            tx, ty = (MIDDLE_SCREEN - MIDDLE).round()()
            M = np.array([[1, 0, tx],[0, 1, ty]], dtype=np.float32)
            image = cv2.warpAffine(image, M, image.shape[:2][::-1])

            image = cv2.circle(image, MIDDLE_SCREEN.round()(), 10, (255, 0, 0), 5)
            normal_image = cv2.circle(normal_image, V2(info=MIDDLE()).round()(), 10, (255, 0, 0), 5)
            deep = 1 - abs(deep) * (1 / right_deep)
            deep = deep if deep > 0 else 0
            print(deep)
            M = cv2.getRotationMatrix2D(MIDDLE_SCREEN.round()(), rotation, deep)          #abs(2-(1/right_deep * deep))
            image = cv2.warpAffine(image, M, image.shape[:2][::-1])
            cv2.imshow('HandsCamera', image)
            cv2.imshow('NHandsCamera', normal_image)
            if cv2.waitKey(1) & 0xFF == 120:
                break
    cam.release()

main()