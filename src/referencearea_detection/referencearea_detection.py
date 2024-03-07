import math
import cv2
import time
from env import PATH

def find_centeroid_white_Area(frame):

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Threshold the frame to get the white areas
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # You might need to adjust the threshold value

    # Compute the moments of the binary image
    moments = cv2.moments(binary)

    # Ensure the area is not zero to avoid division by zero
    if moments['m00'] != 0:
        # Calculate the x and y coordinates of the centroid
        cX = int(moments['m10'] / moments['m00'])
        cY = int(moments['m01'] / moments['m00'])
    else:
        cX, cY = None, None

    return cX,cY

def find_circle_center(frame):

    # Convert the image to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to remove noise and smooth the image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold the image to create a binary image for contour detection
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour, which should be the black circle
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate the moments of the largest contour to find the center
    M = cv2.moments(largest_contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = None, None

    return cX, cY-55


def calculate_angle(frame):
    pt1 = find_centeroid_white_Area(frame)
    pt2 = find_circle_center(frame)

    # Calculate the difference between the two points
    delta_x = pt2[0] - pt1[0]
    delta_y = pt2[1] - pt1[1]

    # Calculate the angle in radians and then convert to degrees
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)

    return int(angle_degrees)+180

def get_image_by_angle(angle,mp4path):
    cap = cv2.VideoCapture(mp4path)
    while cap.isOpened():
        ret, frame = cap.read()
        if calculate_angle(frame) == angle:
            return frame
        if not ret:
            break



