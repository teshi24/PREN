PFAD = 'C:\\Users\\Nicolas\\Documents\\Python Scripts\\PREN\\testdaten\\video.mp4'
import cv2
import numpy as np


# Load the video
video_path = PFAD
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()

    # If the frame was not grabbed, then we have reached the end of the stream
    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Threshold the frame to get the white areas
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # You might need to adjust the threshold value

    # Compute the moments of the binary image
    moments = cv2.moments(binary)

    # Ensure the area is not zero to avoid division by zero
    if moments['m00'] != 0:
        # Calculate the x and y coordinates of the centroid
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
    else:
        cx, cy = None, None

    # If centroid is found, draw it on the frame
    if cx is not None and cy is not None:
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    # Display the frame with the centroid
    cv2.imshow('Video with Centroid', frame)

    # Press 'q' to exit the video window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

