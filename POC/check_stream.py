"""
@file morph_lines_detection.py
@brief Use morphology transformations for extracting horizontal and vertical lines sample code
"""
import logging
import math

import numpy as np
import sys
import cv2 as cv

from src.frame_analyzer.data_types import Color, Cube


def show_wait_destroy(winname, img):
    cv.imshow(winname, img)
    cv.moveWindow(winname, 500, 0)
    cv.waitKey(0)
    cv.destroyWindow(winname)

def draw_cube(cnt, cube, cv, frame):
    cv.rectangle(frame, cube.left_top, cube.right_bottom, cube.color.rgb_value, 2)
    cube.log_values()
    cv.circle(frame, cube.center, 1, (255, 255, 255), -1)
    cv.putText(frame, cube.color.color_name, cube.left_top, cv.FONT_HERSHEY_SIMPLEX, 0.7, cube.color.rgb_value, 2)
    draw_contours(cnt, cv, frame)
    cv.imshow('Test', frame)
    while cv.waitKey(1) & 0xFF != ord('q'):
        continue


def draw_contours(cnt, cv, frame):
    epsilon = 0.04 * cv.arcLength(cnt, True)
    approx = cv.approxPolyDP(cnt, epsilon, True)
    cv.drawContours(frame, [approx], -1, (255, 255, 255), 2)


def find_centeroid_white(image):
    # Convert image to HSV color space
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Define range of white color in HSV
    # These values can be adjusted to be more specific for the white color in the images
    lower_white = np.array([0, 0, 168], dtype=np.uint8)
    upper_white = np.array([172, 111, 255], dtype=np.uint8)

    # Threshold the HSV image to get only white colors
    mask = cv.inRange(hsv, lower_white, upper_white)

    # Find contours in the mask
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Filter out very small contours that are unlikely to be the white area
    contours = [cnt for cnt in contours if cv.contourArea(cnt) > 1000]
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        draw_cube(contour, Cube(Color.RED, x, y, w, h), cv, image)

    # Assuming the largest contour is the white area
    largest_contour = max(contours, key=cv.contourArea)

    x, y, w, h = cv.boundingRect(largest_contour)
    draw_cube(largest_contour, Cube(Color.RED, x, y, w, h), cv, image)

    # Compute the centroid of the largest contour
    moments = cv.moments(largest_contour)
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
        cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00
    else:
        # Set centroid to the center of the image if contour is not found
        cx, cy = image.shape[1] // 2, image.shape[0] // 2

    return cx, cy,

def calculate_angle(frame):
    pt1 = find_centeroid_white(frame)
    pt2 = 641, 277  # TODO Dynamic or Config File

    # Calculate the difference between the two points
    delta_x = pt2[0] - pt1[0]
    delta_y = pt2[1] - pt1[1]

    # Calculate the angle in radians and then convert to degrees
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)

    return int(angle_degrees) + 180

def main(argv):
    # [load_image]
    # Check number of arguments
    i = 155
    while i < 161:
        # Load the image
        src = cv.imread(f'D:/source/PREN/test_frame_{i}.jpg', cv.IMREAD_COLOR)
        # Check if image is loaded fine
        # if src is None:
        #     continue
        # Show source image
        # cv.imshow("src", src)
        print(f'frame: {i}, angle: {calculate_angle(src)}')

        i += 1

    print('done')

    # [load_image]
    # [gray]
    # Transform source image to gray if it is not already
    # if len(src.shape) != 2:
    #     gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    # else:
    #     gray = src
    # # Show gray image
    # show_wait_destroy("gray", gray)
    # # [gray]
    # # [bin]
    # # Apply adaptiveThreshold at the bitwise_not of gray, notice the ~ symbol
    # gray = cv.bitwise_not(gray)
    # bw = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, \
    #                           cv.THRESH_BINARY, 15, -2)
    # # Show binary image
    # show_wait_destroy("binary", bw)
    # # [bin]
    # # [init]
    # # Create the images that will use to extract the horizontal and vertical lines
    # horizontal = np.copy(bw)
    # vertical = np.copy(bw)
    # # [init]
    # # [horiz]
    # # Specify size on horizontal axis
    # cols = horizontal.shape[1]
    # horizontal_size = cols // 30
    # # Create structure element for extracting horizontal lines through morphology operations
    # horizontalStructure = cv.getStructuringElement(cv.MORPH_RECT, (horizontal_size, 1))
    # # Apply morphology operations
    # horizontal = cv.erode(horizontal, horizontalStructure)
    # horizontal = cv.dilate(horizontal, horizontalStructure)
    # # Show extracted horizontal lines
    # show_wait_destroy("horizontal", horizontal)
    # # [horiz]
    # # [vert]
    # # Specify size on vertical axis
    # rows = vertical.shape[0]
    # verticalsize = rows // 30
    # # Create structure element for extracting vertical lines through morphology operations
    # verticalStructure = cv.getStructuringElement(cv.MORPH_RECT, (1, verticalsize))
    # # Apply morphology operations
    # vertical = cv.erode(vertical, verticalStructure)
    # vertical = cv.dilate(vertical, verticalStructure)
    #
    # # Show extracted vertical lines
    # show_wait_destroy("vertical", vertical)
    # # [vert]
    # # [smooth]
    # # Inverse vertical image
    # vertical = cv.bitwise_not(vertical)
    # show_wait_destroy("vertical_bit", vertical)
    # '''
    # Extract edges and smooth image according to the logic
    # 1. extract edges
    # 2. dilate(edges)
    # 3. src.copyTo(smooth)
    # 4. blur smooth img
    # 5. smooth.copyTo(src, edges)
    # '''
    # # Step 1
    # edges = cv.adaptiveThreshold(vertical, 255, cv.ADAPTIVE_THRESH_MEAN_C, \
    #                              cv.THRESH_BINARY, 3, -2)
    # show_wait_destroy("edges", edges)
    # # Step 2
    # kernel = np.ones((2, 2), np.uint8)
    # edges = cv.dilate(edges, kernel)
    # show_wait_destroy("dilate", edges)
    # # Step 3
    # smooth = np.copy(vertical)
    # # Step 4
    # smooth = cv.blur(smooth, (2, 2))
    # # Step 5
    # (rows, cols) = np.where(edges != 0)
    # vertical[rows, cols] = smooth[rows, cols]
    # # Show final result
    # show_wait_destroy("smooth - final", vertical)
    # [smooth]
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
