import cv2
import numpy as np


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


# Farbgrenzen definieren
blue_lower = np.array([100, 150, 100])
blue_upper = np.array([140, 255, 255])
red_lower1 = np.array([0, 120, 70])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 120, 70])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([15, 150, 100])
yellow_upper = np.array([35, 255, 255])

# VideoCapture-Objekt erstellen und Video-Datei laden
cap = cv2.VideoCapture('C:\\Users\\Nicolas\\Documents\\Python Scripts\\PREN\\testdaten\\video.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    blue_contours = detect_color(frame, blue_lower, blue_upper)
    red_contours1 = detect_color(frame, red_lower1, red_upper1)
    red_contours2 = detect_color(frame, red_lower2, red_upper2)
    yellow_contours = detect_color(frame, yellow_lower, yellow_upper)

    red_contours = red_contours1 + red_contours2

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, "Blue", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, "Red", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(frame, "Yellow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
