import cv2
import numpy as np

colorKeys = {'red': ((0, 60, 60), (10, 255, 255), (170, 70, 50), (180, 255, 255)),
             'yellow': ((20, 50, 50), (40, 255, 255)),
             'blue': ((78, 158, 84), (145, 255, 255))}

colors = {'red': (0, 0, 255),
          'yellow': (0, 255, 255),
          'blue': (255, 0, 0)}

DEBUG = True

class ImageProcessing():

    def __init__(self, image):
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        self.__img = image
        self.__img_hsv = img_hsv

    def image_size(self):
        return self.__img.shape

    def image_hsv(self):
        return self.__img_hsv

    def empty_image(self):
        h, w, c = self.image_size()
        res = np.zeros((h, w, 3), np.uint8)
        res[:] = (0, 0, 0)
        return res[:]

    def image_copy(self):
        return self.__img.copy()


    def draw_on_image(self):
        print("imp")
        ## implement

class Kontur():
    def __init__(self, img: ImageProcessing, color):
        self.__img = img
        self.__color = color
        self.__polygon_edges = []
        self.__contour_centers = []

        mask = None
        for i in range(int(len(colorKeys[color]) / 2)):
            temp = cv2.inRange(self.__img.image_hsv(), colorKeys[color][int(i * 2)], colorKeys[color][int(i * 2 + 1)])
            if mask is None:
                mask = temp
            else:
                mask = cv2.add(temp, mask)

        if DEBUG:
            self.save(mask, "mask")

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if DEBUG:
            res = self.__img.empty_image()

        h, w, c = self.__img.image_size()
        min_area = h * w / 400
        for cnt in contours:

            area = cv2.contourArea(cnt)
            if area < min_area:
                continue

            epsilon = 0.04 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if DEBUG:
                cv2.drawContours(res, [approx], -1, colors[self.__color], 3)

            for app in approx:
                self.__polygon_edges.append((app[0][0], app[0][1]))
                if DEBUG:
                    cv2.circle(res, (app[0][0], app[0][1]), 10, colors[self.__color], -1)

            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                self.__contour_centers.append((cX, cY))
            else:
                self.__contour_centers.append((30, 30))

        if DEBUG:
            self.save(res, "contours")

    def save(self, img, name):
        img_name = "./dist/{}_{}.jpg".format(self.__color, name)
        cv2.imshow(img_name, img)
        cv2.imwrite(img_name, img)
        cv2.waitKey()

    def polygon_points(self):
        return self.__polygon_edges

    def contour_centers(self):
        return self.__contour_centers

    # yellow = Kontur(img_hsv, 'yellow')
    # blue = Kontur(img_hsv, 'blue')
