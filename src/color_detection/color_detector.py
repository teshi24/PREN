import time

import cv2
import numpy as np

blue_lower = np.array([100, 150, 100])
blue_upper = np.array([140, 255, 255])
red_lower1 = np.array([0, 120, 70])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 120, 70])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([15, 150, 100])
yellow_upper = np.array([35, 255, 255])


def detect_color(image, lower_bound, upper_bound, min_area=1000):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Morphologische Operationen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtern der Konturen nach Fläche
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    return filtered_contours


def printTheValues(color, x, y, w, h):
    print("----------------------")
    print("color: " + color)
    print("x: " + str(x))
    print("y: " + str(y))
    print("w: " + str(w))
    print("h: " + str(h))
    print("center       (cx, cy):       (" + str(int(x + w/2)) + ", " + str(int(y + h/2)) +")")
    print("left top     (x, y):         (" + str(x) + ", " + str(y) +")")
    print("right top    (x + w, y):     (" + str(x + w) + ", " + str(y) +")")
    print("right bottom (x + w, y + h): (" + str(x + w) + ", " + str(y + h) +")")
    print("left bottom  (x, y + h):     (" + str(x) + ", " + str(y + h) +")")

def getColorOfFrame(frame, cv2):
    blue_contours = detect_color(frame, blue_lower, blue_upper)
    red_contours1 = detect_color(frame, red_lower1, red_upper1)
    red_contours2 = detect_color(frame, red_lower2, red_upper2)
    yellow_contours = detect_color(frame, yellow_lower, yellow_upper)

    red_contours = red_contours1 + red_contours2

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        printTheValues("blue", x, y, w, h)
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        cv2.circle(frame, (cx, cy), 1, (255, 255, 255), -1)
        cv2.circle(frame, (x + w, y), 1, (255, 255, 255), -1)
        cv2.putText(frame, "Blue", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        getCenter(cnt, frame)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        printTheValues("red", x, y, w, h)
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        cv2.circle(frame, (cx, cy), 1, (255, 255, 255), -1)
        cv2.circle(frame, (x, y + h), 1, (255, 255, 255), -1)
        cv2.putText(frame, "Red", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        getCenter(cnt, frame)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        printTheValues("yellow", x, y, w, h)
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        cv2.circle(frame, (cx, cy), 1, (255, 255, 255), -1)
        cv2.putText(frame, "Yellow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        getCenter(cnt, frame)

    cv2.imshow('Video', frame)
    while (cv2.waitKey(1) & 0xFF != ord('q')):
        continue
    return [blue_contours, red_contours, yellow_contours, cv2]


def getCenter(cnts, frame):
    # loop over the contours
   # print(cnts)
    for c in cnts:
        # print(c)
        # compute the center of the contour
        M = cv2.moments(c)
        #print(M)
        if (M["m00"] == 0):
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(frame, "center", (cX - 20, cY - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # show the image
        cv2.imshow("Image", frame)
        cv2.waitKey(0)


def getFrame(PATH):
    # VideoCapture-Objekt erstellen und Video-Datei laden
    cap = cv2.VideoCapture(PATH)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        [blue_contours, red_contours, yellow_contours, cv3] = getColorOfFrame(frame, cv2)
        # print(blue_contours)
        # print(red_contours)
        # print(yellow_contours)

        return frame

    cap.release()
    cv2.destroyAllWindows()
