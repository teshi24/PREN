import queue
import threading
from abc import abstractmethod, ABC

import cv2

from env import logging_level, dummies, PATH
import logging
from frame_analyzer import position_analyzer as pa
from datetime import datetime
import json
import os
import time

# Module importieren
from path_finder.path_finder import find_best_path
from referencearea_detection.referencearea_detection import get_image_and_angle

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)


def write_to_file(positions_json, i):
    file_name = f"positions_config_{i}.json"
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(positions_json, file)


def analyze_frames(frame_queue: queue.Queue, positions: {}):
    found_positions = []
    for i in range(4):
        (frame, angle, intersection_point, edges) = frame_queue.get()
        logging.info('position analysis starting')
        logging.info(f'img {i}, angle {angle}')
        found_positions.append(pa.analyze_frame(frame, angle, intersection_point, edges))

    positions.update(pa.combine_positions(found_positions))


def show_energy_consumption_dummy(energy_consumption):
    print(f"Dummy update_display: Energy Consumption: {energy_consumption} wh")


def update_progress_bar_dummy(energy_consumption_event):
    i = 0
    while not energy_consumption_event.is_set():
        print(f"Progressbar bei {i} %")
        time.sleep(10)
        i += 1
    print(f"Progressbar bei 100 %")
    print(f'energy consumption: {energy_consumption_event.energy_consumption}')


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
    def wait_for_energy_consumption(self):
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

    def wait_for_energy_consumption(self):
        while True:
            feedback = self.bus.read_byte(self.arduino_i2c_address)
            if feedback:
                return


class DummySignalInterface(SignalInterface):
    def wait_for_start_signal(self):
        print("Press 's' to simulate the retrieval of the start signal from the machine")
        while True:
            key = input()
            if key == 's':
                return

    def wait_for_energy_consumption(self):
        print(
            "Press 'f' to to simulate the retrieval of the energy consumption from the machine (which is also the 'finished' signal)")
        while True:
            key = input()
            if key == 'f':
                return 100


class Main:
    def __init__(self, signal_interface, progress_bar_func, energy_func):
        self.signal_interface = signal_interface
        self.progress_bar_func = progress_bar_func
        self.energy_func = energy_func

    def main(self):
        while True:
            self.signal_interface.wait_for_start_signal()

            energy_consumption_event = threading.Event()
            progress_bar_thread = threading.Thread(target=self.progress_bar_func, args=[energy_consumption_event])
            progress_bar_thread.start()

            logging.info('open queue')
            frame_queue = queue.Queue()

            logging.info('fill queue')

            running = threading.Event()
            running.set()
            find_frame_thread = threading.Thread(target=get_image_and_angle, args=(frame_queue, running))
            find_frame_thread.start()

            positions = {}
            analyze_frames_thread = threading.Thread(target=analyze_frames, args=(frame_queue, positions))
            analyze_frames_thread.start()

            analyze_frames_thread.join()
            running.clear()

            path = find_best_path(positions)

            # todo: send path to machine
            # todo: send config to API

            positions_json = {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'config': positions, 'path': path}
            logging.debug('write to file...')
            write_to_file(positions_json, 10)

            logging.info('positions written to file')

            # ensure that this thread gets closed
            find_frame_thread.join()

            energy_consumption = self.signal_interface.wait_for_energy_consumption()
            energy_consumption_event.energy_consumption = energy_consumption
            energy_consumption_event.set()


if dummies:
    signalInterface = DummySignalInterface()
    progress_bar_func = update_progress_bar_dummy
    energy_func = show_energy_consumption_dummy
else:
    raise NotImplementedError('need to connect the IC2-IF ;)')
    signalInterface = I2CSignalInterface(None, None)
    # display module nur importieren, wenn sie genutzt werden sollen
    # - dann müssen gewisse packages nur auf raspy installiert werden
    from Display.progress_bar import show_progress_bar
    from Display.energy_consumption import show_energy_consumption

    progress_bar_func = show_progress_bar
    energy_func = show_energy_consumption

Main(signalInterface, progress_bar_func, energy_func).main()
