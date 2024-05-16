import queue
import threading
from abc import abstractmethod, ABC

import cv2

from env import logging_level, PATH
import logging
from frame_analyzer import position_analyzer as pa
from datetime import datetime
import json
import os

from src.path_finder.path_finder import find_best_path
from src.referencearea_detection.referencearea_detection import get_image_and_angle

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)
## todo: remove dummies / set it to False
dummys = True


def write_to_file(positions_json, i):
    file_name = f"positions_config_{i}.json"
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(positions_json, file)


def analyze_frames(frame_queue: queue):
    (frame, angle) = frame_queue.get()
    logging.info('img 0')
    logging.debug(angle)

    (frame1, angle1) = frame_queue.get()
    logging.info('img 1')
    logging.debug(angle1)

    (frame2, angle2) = frame_queue.get()
    logging.info('img 2')
    logging.debug(angle2)

    (frame3, angle3) = frame_queue.get()
    logging.info('img 3')
    logging.debug(angle3)

    logging.info('position analysis starting')
    positions = pa.analyze_cube_positions_per_frames(frame, angle, frame1, angle1, frame2, angle2, frame3, angle3)
    logging.info('position analysis done')

    # todo: consider to move this stuff out of the thread
    path = find_best_path(positions)

    # todo: send path to machine
    # todo: send config to API

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions, 'path': path}
    logging.debug('write to file...')
    write_to_file(positions_json, 10)

    logging.info('positions written to file')


def get_image_and_angle_dummy_from_video(result_queue: queue.Queue, running: threading.Event):
    logging.debug('trying to get image')
    # VideoCapture-Objekt erstellen und Video-Datei laden
    cap = cv2.VideoCapture(PATH)

    logging.info(f'analyzing video {PATH}')
    logging.debug('image analysis starting....')

    frame_count = 0
    angle = 0
    while running.is_set():
        if angle > 270:
            break

        ret, frame = cap.read()
        if not ret:
            break

        if frame_count != 0:
            frame_count = frame_count - 1
            continue
        else:
            frame_count = 220

        result_queue.put((frame, angle))

        angle = angle + 90
    try:
        cap.release()
        cv2.destroyAllWindows()
    finally:
        pass


class SignalInterface(ABC):
    @abstractmethod
    def wait_for_start_signal(self):
        pass

    @abstractmethod
    def wait_for_feedback(self):
        pass


class I2CSignalInterface(SignalInterface):
    # todo: use the real I2CIF, probably need to adapt stuff here
    # self.bus = smbus.SMBus(1)  # I2C bus 1
    # self.arduino_i2c_address = 'your_arduino_i2c_address'  # Replace with your Arduino's I2C address

    def __init__(self, bus, arduino_i2c_address):
        self.bus = bus
        self.arduino_i2c_address = arduino_i2c_address

    def wait_for_start_signal(self):
        while True:
            start_signal = self.bus.read_byte(self.arduino_i2c_address)
            if start_signal:
                return

    def wait_for_feedback(self):
        while True:
            feedback = self.bus.read_byte(self.arduino_i2c_address)
            if feedback:
                return

class DummySignalInterface(SignalInterface):
    def wait_for_start_signal(self):
        print("Press 's' to send start signal")
        while True:
            key = input()
            if key == 's':
                return

    def wait_for_feedback(self):
        print("Press 'f' to send feedback")
        while True:
            key = input()
            if key == 'f':
                return

class Main:
    def __init__(self, signal_interface, frame_detection_func):
        self.signal_interface = signal_interface
        self.frame_detection_func = frame_detection_func

    def main(self):
        while True:
            self.signal_interface.wait_for_start_signal()

            logging.info('open queue')
            frame_queue = queue.Queue()

            logging.info('fill queue')

            running = threading.Event()
            running.set()
            find_frame_thread = threading.Thread(target=self.frame_detection_func, args=(frame_queue, running))
            find_frame_thread.start()

            analyze_frames_thread = threading.Thread(target=analyze_frames, args=[frame_queue])
            analyze_frames_thread.start()

            analyze_frames_thread.join()
            running.clear()
            find_frame_thread.join()

            self.signal_interface.wait_for_feedback()

if dummys:
    signalInterface = DummySignalInterface()
    frame_detection_func = get_image_and_angle_dummy_from_video
else:
    raise NotImplementedError('need to connect the IC2-IF ;)')
    signalInterface = I2CSignalInterface(None, None)
    frame_detection_func = get_image_and_angle

Main(signalInterface, frame_detection_func).main()
