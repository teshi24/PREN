# -*- coding: utf-8 -*-

from os import environ
import logging

PATH0 = 'D:\\source\\PREN\\testdata\\pren.videooo.mp4'
PATH1 = 'D:\\source\\PREN\\testdata\\pren_4_wuerfel.mp4'
PATH2 = 'D:\\source\\PREN\\testdata\\pren_5_wuerfel_gleichfarbene_nebeneinander.mp4'
PATH3 = 'D:\\source\\PREN\\testdata\\pren_5_wuerfel_gleichfarbene_nebeneinander_flacher.mp4'
PATH4 = 'D:\\source\\PREN\\testdata\\pren_5_wuerfel_gleichfarbene_nebeneinander_flaeche_aufgestellt.mp4'
PATH5 = 'D:\\source\\PREN\\testdata\\pren_6_wuerfel_gleichfarbene_aufeinander.mp4'

PATHS_specialCases = [
    PATH0, PATH1, PATH2, PATH3, PATH4, PATH5
]

PATH_OFFICIAL_1 = 'D:\\source\\PREN\\testdata\\pren_cube_01.mp4'
PATH_OFFICIAL_2 = 'D:\\source\\PREN\\testdata\\pren_cube_02.mp4'
PATH_OFFICIAL_3 = 'D:\\source\\PREN\\testdata\\pren_cube_03.mp4'

PATHS = [
    PATH_OFFICIAL_1,
    PATH_OFFICIAL_2,
    PATH_OFFICIAL_3
]

PATH = PATH_OFFICIAL_1
PATH = PATH_OFFICIAL_2
PATH = PATH_OFFICIAL_3

logging_level = logging.INFO
logging_level = logging.DEBUG

dummy_image_paths = [
    'D:\\source\\PREN\\test_frame_92.jpg',
    'D:\\source\\PREN\\test_frame_257.jpg',
    'D:\\source\\PREN\\test_frame_417.jpg',
    'D:\\source\\PREN\\test_frame_581.jpg',
]


# PATHS = PATHS_specialCases