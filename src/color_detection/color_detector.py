from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np

# HSV filters
blue_lower = np.array([75, 95, 84])
blue_upper = np.array([145, 255, 255])
red_lower1 = np.array([0, 130, 130])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 70, 50])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([20, 140, 50])
yellow_upper = np.array([50, 255, 255])


def detect_color(image, lower_bound1, upper_bound1, lower_bound2=None, upper_bound2=None, min_area=700):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound1, upper_bound1)
    if (lower_bound2 is not None):
        mask = cv2.add(cv2.inRange(hsv, lower_bound2, upper_bound2), mask)

    # Morphologische Operationen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    # contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # Filtern der Konturen nach Fläche
    # ih, iw, ic = image.shape
    # min_area = ih * iw / 400
    # min_area = 500
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    return filtered_contours


@dataclass
class ColorData:
    color_name: str
    rgb_value: tuple


class Color(ColorData, Enum):
    RED = 'red', (0, 0, 255)
    BLUE = 'blue', (255, 0, 0)
    YELLOW = 'yellow', (0, 255, 255)
    NONE = '', ()


class Cube():
    def __init__(self, color, x, y, w, h):
        self.color = color
        self.x = x
        self.y = y
        self.__w = w
        self.__h = h
        self.cx = int(x + w / 2)
        self.cy = int(y + h / 2)
        self.center = (self.cx, self.cy)
        self.left_top = (x, y)
        self.right_top = (x + w, y)
        self.right_bottom = (x + w, y + h)
        self.left_bottom = (x, y + h)

    def printValues(self):
        print("----------------------")
        print("color: " + self.color.color_name)
        print("x: " + str(self.x))
        print("y: " + str(self.y))
        print("w: " + str(self.__w))
        print("h: " + str(self.__h))
        print("center       (cx, cy):       " + str(self.center))
        print("left top     (x, y):         " + str(self.left_top))
        print("right top    (x + w, y):     " + str(self.right_top))
        print("right bottom (x + w, y + h): " + str(self.right_bottom))
        print("left bottom  (x, y + h):     " + str(self.left_bottom))


class PositionIdentifier():
    def __init__(self, calibrationCube: Cube):
        self.calibrationCube = calibrationCube
        self.toleranceXAxis = 35
        self.toleranceYAxis = 85

    def isCubeAtPosition(self, cube: Cube):
        return (self.__is_value_in_range(cube.x, self.calibrationCube.x, self.toleranceXAxis) and
                self.__is_value_in_range(cube.y, self.calibrationCube.y, self.toleranceYAxis) and
                self.__is_value_in_range(cube.cx, self.calibrationCube.cx, self.toleranceXAxis) and
                self.__is_value_in_range(cube.cy, self.calibrationCube.cy, self.toleranceYAxis))

    def __is_value_in_range(self, value: int, average: int, delta: int):
        lower_bound = average - delta
        upper_bound = average + delta
        return lower_bound <= value <= upper_bound


# obere Fläche  0°             obere Fläche  90°                              obere Fläche  180°           obere Fläche  270°
# +---+---+                    +---+---+                                      +---+---+                    +---+---+
# | 7 | 6 |                    | 8 | 7 |                                      | 5 | 8 |                    | 6 | 5 |
# +---+---+                    +---+---+                                      +---+---+                    +---+---+
# | 8 | 5 |                    | 5 | 6 |                                      | 6 | 7 |                    | 7 | 8 |
# +---+---+                    +---+---+                                      +---+---+                    +---+---+
# untere Fläche                untere Fläche                                  untere Fläche                untere Fläche
# +---+---+                    +---+---+                                      +---+---+                    +---+---+
# | 3 | 2 |                    | 4 | 3 | weisser Bereich      weisser Bereich | 1 | 4 |                    | 2 | 1 |
# +---+---+ --                 +---+---+ --                                -- +---+---+                  --+---+---+
# | 4 | 1 |                    | 1 | 2 |                                      | 2 | 3 |                    | 3 | 4 |
# +---+---+                    +---+---+                                      +---+---+                    +---+---+
#     |  weisser Bereich                                                                       weisser Bereich |

defaultConfig = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None
}

# todo: add calibration algorithm
# calibratedPositions = {
#     1: PositionIdentifier(Cube(Color.NONE, 967, 411, 182, 162)),
#     2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98)),
#     3: None,  # PositionIdentifier(Cube(Color.NONE, 967, 411, 196, 100)),
#     4: PositionIdentifier(Cube(Color.NONE, 781, 416, 184, 158)),
#     5: PositionIdentifier(Cube(Color.NONE, 964, 183, 210, 258)),
#     6: PositionIdentifier(Cube(Color.NONE, 952, 100, 196, 100)),
#     7: PositionIdentifier(Cube(Color.NONE, 780, 98, 186, 126)),
#     8: PositionIdentifier(Cube(Color.NONE, 770, 177, 200, 274)),
# }

# extra sortiert, damit andere Reihenfolge entdeckt wird
calibratedPositions = {
    8: PositionIdentifier(Cube(Color.NONE, 770, 177, 200, 274)),
    5: PositionIdentifier(Cube(Color.NONE, 964, 183, 210, 258)),
    7: PositionIdentifier(Cube(Color.NONE, 780, 98, 186, 126)),
    6: PositionIdentifier(Cube(Color.NONE, 952, 100, 196, 100)),
    3: None,  # PositionIdentifier(Cube(Color.NONE, 967, 411, 196, 100)),
    2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98)),
    1: PositionIdentifier(Cube(Color.NONE, 967, 411, 182, 162)),
    4: PositionIdentifier(Cube(Color.NONE, 781, 416, 184, 158)),
}


# for i in range(0, 8):
#     calibrated_position = calibratedPositions.get(i + 1)
#     if calibrated_position is None:
#         continue
#     calibrated_position.calibrationCube.printValues()


def analyzePositionsInOneFrame(cubes: [Cube]):
    positions = defaultConfig.copy()

    for cube in cubes:
        print("color: " + str(cube.color.color_name) + ", x: " + str(cube.x) + ", y: " + str(cube.y) + ", center: " + str(cube.center))
        for key, position_identifier in calibratedPositions.items():
            print("calibratedPosition: " + str(position_identifier))
            if positions[key] is None and position_identifier is not None and position_identifier.isCubeAtPosition(cube):
                positions[key] = cube.color
                break

    print("detected Positions:")
    print(positions)


def getCubesFromFrame(frame, cv2):
    print("----------- getColorOfFrame -----------")
    blue_contours = detect_color(frame, blue_lower, blue_upper)
    red_contours = detect_color(frame, red_lower1, red_upper1, red_lower2, red_upper2)
    yellow_contours = detect_color(frame, yellow_lower, yellow_upper)

    cubes = []

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.BLUE, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.RED, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.YELLOW, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    cv2.imshow('Video', frame)
    while (cv2.waitKey(1) & 0xFF != ord('q')):
        continue
    return [cv2, cubes]


def drawCube(cnt, cube, cv2, frame):
    cv2.rectangle(frame, cube.left_top, cube.right_bottom, cube.color.rgb_value, 2)
    cube.printValues()
    cv2.circle(frame, cube.center, 1, (255, 255, 255), -1)
    cv2.putText(frame, cube.color.color_name, cube.left_top, cv2.FONT_HERSHEY_SIMPLEX, 0.7, cube.color.rgb_value, 2)
    drawContours(cnt, cv2, frame)
    return cv2


def drawContours(cnt, cv2, frame):
    epsilon = 0.04 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    print(approx)
    cv2.drawContours(frame, [approx], -1, (255, 255, 255), 2)


def getFrame(PATH):
    # VideoCapture-Objekt erstellen und Video-Datei laden
    cap = cv2.VideoCapture(PATH)

    frameCount = 0
    roundCount = 4
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if roundCount <= 0:
            break

        if frameCount != 0:
            frameCount = frameCount - 1
            continue
        else:
            # todo: check with angle detector whether we are good
            frameCount = 220
            roundCount = roundCount - 1
            print(roundCount)

        [cv3, cubes] = getCubesFromFrame(frame, cv2)
        analyzePositionsInOneFrame(cubes)

    return frame
    cap.release()
    cv2.destroyAllWindows()
